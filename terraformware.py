#!/usr/bin/python
#
""" requirements through pip:
    - pyhcl
    - infoblox-client
    - python-terraform
"""
import os
import ast
import glob
import json
import argparse
import ConfigParser
import hcl
from infoblox_client import connector
from infoblox_client import objects
from jinja2 import Environment
from jinja2 import FileSystemLoader
from python_terraform import Terraform
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

CRED_FILE_CONTENT = """[tf_credentials]\n
# Vcenter/Infoblox username (AD user) <string>: your_username
username = your_username\n
# Vcenter/Infoblox password (AD password) <string>: your_password
password = your_secret_pass_here\n
# Infoblox server <string>: infblox fqdn
iblox_server = infoblox.win.dante.org.uk\n
# Consul server <string>: consul server fqdn
consul_server = puppet01.geant.net\n
"""


def parse():
    """parse arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument('-var-file', dest='vfile', action='append', default=[])
    parser.add_argument('-t', '--test', action='store_true')
    parser.add_argument('-s', '--showvars', action='store_true')

    return parser.parse_args()


def load_variables(filenames):
    """load terraform variables"""

    variables = {}

    for terrafile in glob.glob('./*.tf'):
        with open(terrafile) as data_fh:
            data = hcl.load(data_fh)
            for key, value in data.get('variable', {}).iteritems():
                if 'default' in value:
                    variables.update({key: value['default']})

    for varfile in filenames:
        with open(varfile) as var_fh:
            data = hcl.load(var_fh)
            variables.update(data)

    return variables


def render(j2_template, j2_context):
    """render jinja templates"""

    path, filename = os.path.split(j2_template)
    return Environment(
        loader=FileSystemLoader(path or './')
    ).get_template(filename).render(j2_context)


def terraform_apply(username, password):
    """run terraform"""

    tform = Terraform(working_dir='.')
    tform.apply(refresh=False, var={
        'VSPHERE_USER': username,
        'VSPHERE_PASSWORD': password
        })


class Iblox(object):
    """manage infoblox entries"""
    config = ConfigParser.RawConfigParser()
    config.readfp(open(CRED_CONF))
    user = CONFIG.get('tf_credentials', 'username')
    password = CONFIG.get('tf_credentials', 'password')
    server = CONFIG.get('tf_credentials', 'iblox_server')

    def __init__(self, record, ipv4, ipv6):
        self.record = record
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.opts = {
            'host': self.server,
            'username': self.user,
            'password': self.password
            }
        self.conn = connector.Connector(self.opts)

    def query_host(self):
        """query for host record"""
        try:
            host_rec = self.conn.get_object(
                'record:host', {'name': self.record})[0]
        except TypeError:
            return None
        else:
            return host_rec

    # def query_a(self):
    #     """query for A record"""
    #     try:
    #         a_rec = self.conn.get_object(
    #             'record:a', {'name': self.record})[0]
    #     except TypeError:
    #         return None
    #     else:
    #         return a_rec

    # def query_aaaa(self):
    #     """query for AAAA record"""
    #     try:
    #         aaaa_rec = self.conn.get_object(
    #             'record:aaaa', {'name': self.record})[0]
    #     except TypeError:
    #         return None
    #     else:
    #         return aaaa_rec

    def rebuild(self):
        """delete entry and create it again"""

        host_entry = self.query_host()
        # a_entry = self.query_a()
        # aaaa_entry = self.query_aaaa()

        if host_entry:
            self.conn.delete_object(host_entry['_ref'])

        # the remaining part will be carried out by terraform.
        # if a_entry:
        #     self.conn.delete_object(a_entry['_ref'])
        # if aaaa_entry:
        #     self.conn.delete_object(aaaa_entry['_ref'])
        # { "name":"wapi.test.org",
        #   "ipv4addrs":[
        #       {
        #          "ipv4addr":"func:nextavailableip:10.1.1.0/24"
        #       }
        #     ]
        # }


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    CRED_CONF = os.path.join(os.environ['HOME'], '.tf_credentials.conf')

    if os.access(CRED_CONF, os.W_OK):
        CONFIG = ConfigParser.RawConfigParser()
        CONFIG.readfp(open(CRED_CONF))
        USERNAME = CONFIG.get('tf_credentials', 'username')
        PASSWORD = CONFIG.get('tf_credentials', 'password')
        IBLOX_SERVER = CONFIG.get('tf_credentials', 'iblox_server')
    else:
        CRED_FILE = open(CRED_CONF, 'w+')
        CRED_FILE.write(CRED_FILE_CONTENT)
        CRED_FILE.close()
        print "the file {0} has been created".format(CRED_CONF)
        print "fill in proper values and run the script again"
        os.sys.exit()

    if not os.access('./main.j2', os.R_OK):
        print 'please run the script from terraform directory'
        os.sys.exit()

    ARGS = parse()

    # jinja renderer taken from: https://github.com/Crapworks/terratools
    CONTEXT = load_variables(ARGS.vfile)
    if ARGS.showvars:
        print json.dumps(CONTEXT, indent=2)
        print CONTEXT

    for template in glob.glob('./*.j2'):
        rendered_filename = '{}.tf'.format(os.path.splitext(template)[0])
        if ARGS.test:
            print render(template, CONTEXT)
        else:
            with open(rendered_filename, 'w') as fh:
                fh.write(render(template, CONTEXT))
            iblox_vars = ast.literal_eval(json.dumps(CONTEXT))
            INSTANCES = iblox_vars['instances']
            for virtual_machine in range(1, int(INSTANCES) + 1):
                ipv4_address = iblox_vars[str(virtual_machine)]['ipv4_address']
                ipv6_address = iblox_vars[str(virtual_machine)]['ipv6_address']
                host_name = iblox_vars[str(virtual_machine)]['hostname']
                print host_name
                Iblox(host_name, ipv4_address, ipv6_address).rebuild()

            # iblox(args.vfile)
            # terraform_apply(USERNAME, PASSWORD)
