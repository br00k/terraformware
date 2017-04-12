#!/usr/bin/python
#
"""
  requirements through pip:
    - pyhcl
    - infoblox-client
    - python-terraform
    - ast, requests, configparser, jinja2, argparse, json
  TODO:
    - add External/Internal view for Infoblox (now we've hardcoded External)
    - add some progress and time for terraform execution
"""
import os
import ast
import json
import argparse
import ConfigParser
import hcl
from jinja2 import Template
from python_terraform import Terraform
from infoblox_client import connector
from infoblox_client import objects
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

CRED_CONF = os.path.join(os.environ['HOME'], '.terraformware.conf')
TF_RC_CONF = os.path.join(os.environ['HOME'], '.terraformrc')

TF_RC_CONTENT = """# Infoblox provider\n#
# download URL: https://github.com/prudhvitella/terraform-provider-infoblox/releases/
#
providers {
  infoblox = "/path/to/terraform-provider-infoblox"
}\n
"""

CRED_FILE_CONTENT = """[terraformware]\n
# Vcenter username (AD user) <string>: your_username
vsphere_username = your_username\n
# Vcenter password (AD password) <string>: your_password
vsphere_password = your_secret_pass_here\n
# VSphere server
vsphere_server = chvc01.win.dante.org.uk\n
# Infoblox username <string>: your_username
iblox_username = your_username\n
# Infoblox password <string>: your_password
iblox_password = your_secret_pass_here\n
# Infoblox server <string>: infblox server fqdn
iblox_server = infoblox.win.dante.org.uk\n
# Consul server:port <string>: consul server fqdn:port
consul_server = puppet01.geant.net:8500\n
# Consul access token <string>: consul secret
consul_token = xxxxxxxxxxx\n
"""


def parse():
    """parse arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument('-var-file', dest='vfile', action='append', default=[])
    parser.add_argument('-t', '--test', action='store_true')
    parser.add_argument('-s', '--showvars', action='store_true')
    parser.add_argument('--destroy', action='store_true')

    return parser.parse_args()


def byebye(status=0):
    """remove main.tf"""

    if os.access('./main.tf', os.W_OK):
        os.remove('./main.tf')
    os.sys.exit(status)


def load_variables(filenames, terrafile='./variables.tf'):
    """load terraform variables"""

    variables = {}

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

    global module_dir
    module_dir = os.path.basename(os.getcwd())
    config = ConfigParser.RawConfigParser()
    config.readfp(open(CRED_CONF))

    def custom_dictionary(arg_key, arg_sub_key):
        """return dict value"""
        return j2_context[arg_key][arg_sub_key].split('.')[0]

    def custom_variable(arg_var):
        """return variable"""
        return config.get('terraformware', arg_var)

    def custom_locals(args_global):
        """ return variable defined in the script"""
        return globals()[args_global]

    with open(j2_template, 'r') as my_template:
        template = my_template.read()
    jinja_template = Template(template)
    jinja_template.globals['custom_dictionary'] = custom_dictionary
    jinja_template.globals['custom_variable'] = custom_variable
    jinja_template.globals['custom_locals'] = custom_locals

    return jinja_template.render(**j2_context)


def terraform_run(action, work_dir='.'):
    """run terraform"""

    tform = Terraform(working_dir=work_dir)

    if action == 'destroy':
        print "running terraform destroy..."
        tform.destroy()
    elif action == 'apply':
        print "running terraform apply... (takes a while)"
        tform.apply(refresh=False)


class Iblox(object):
    """manage infoblox entries"""
    config = ConfigParser.RawConfigParser()

    def __init__(self, record, ipv4, ipv6, config=config):
        self.record = record
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.config = config
        self.config.readfp(open(CRED_CONF))
        self.opts = {
            'host': self.config.get('terraformware', 'iblox_server'),
            'username': self.config.get('terraformware', 'iblox_username'),
            'password': self.config.get('terraformware', 'iblox_password')
            }
        self.conn = connector.Connector(self.opts)

    def query_host(self):
        """query for host record"""
        try:
            host_rec = self.conn.get_object('record:host', {'name': self.record})[0]
        except TypeError:
            return None
        else:
            return host_rec

    def query_a(self):
        """query for A record"""
        try:
            a_rec = self.conn.get_object('record:a',
                                         {'name': self.record})[0]
        except TypeError:
            return None
        else:
            return a_rec

    def query_aaaa(self):
        """query for AAAA record"""
        try:
            aaaa_rec = self.conn.get_object('record:aaaa',
                                            {'name': self.record})[0]
        except TypeError:
            return None
        else:
            return aaaa_rec

    def destroy(self):
        """ clean up host entries """
        host_entry = self.query_host()
        a_entry = self.query_a()
        aaaa_entry = self.query_aaaa()

        if host_entry:
            self.conn.delete_object(host_entry['_ref'])
            print "destroyed host record {}".format(self.record)
        if a_entry:
            self.conn.delete_object(a_entry['_ref'])
            print "destroyed A Record for {} with IP {}".format(
                self.record, self.ipv4)
        if aaaa_entry:
            self.conn.delete_object(aaaa_entry['_ref'])
            print "destroyed AAAA record {} with IPv6 {}".format(
                self.record, self.ipv6)

    def rebuild(self):
        """delete entry and create it again
           couple of things:
             - cannot get hostrecord ipv6 to work
             - update_if_exists does not work as expected
             - we need to destroy and create the entry again
        """

        self.destroy()

        try:
            objects.ARecord.create(self.conn, view='External',
                                   name=self.record, ip=self.ipv4)
        except Exception as err:
            print "couldn't create A Record for {} with IP {}: {}".format(
                self.record, self.ipv4, err)
            byebye(1)
        else:
            print "created A Record {} with IP {}".format(self.record,self.ipv4)

        try:
            objects.AAAARecord.create(self.conn, view='External',
                                      name=self.record, ip=self.ipv6)
        except Exception as err:
            print "couldn't create AAAA Record {} with IPv6 {}: {}".format(
                self.record, self.ipv6, err)
            byebye(1)
        else:
            print "created AAAA Record {} with IP {}".format(self.record, self.ipv6)

        print '='*80


if __name__ == '__main__':
    print '='*80
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    TEMPLATE = './terraformware.j2'
    RENDERED_FNAME = 'main.tf'

    if not os.access(CRED_CONF, os.W_OK):
        CRED_FILE = open(CRED_CONF, 'w+')
        CRED_FILE.write(CRED_FILE_CONTENT)
        CRED_FILE.close()
        print "\nThe following file has been created: {0}\n".format(CRED_CONF)
        print "Fill it with proper values and run the script again\n"
        byebye(1)

    if not os.access(TF_RC_CONF, os.W_OK):
        TF_FILE = open(TF_RC_CONF, 'w+')
        TF_FILE.write(TF_RC_CONTENT)
        TF_FILE.close()
        print "\nThe following file has been created: {0}\n".format(TF_RC_CONF)
        print "Fill it with proper values and run the script again\n"
        byebye(1)

    if not os.access(TEMPLATE, os.R_OK):
        print 'please run the script from terraform directory'
        byebye(1)

    ARGS = parse()

    # jinja renderer taken from: https://github.com/Crapworks/terratools
    CONTEXT = load_variables(ARGS.vfile)
    if ARGS.showvars:
        print json.dumps(CONTEXT, indent=2)

    if ARGS.test:
        print render(TEMPLATE, CONTEXT)
    else:
        with open(RENDERED_FNAME, 'w') as fh:
            fh.write(render(TEMPLATE, CONTEXT))
        IBLOX_VARS = ast.literal_eval(json.dumps(CONTEXT))
        INSTANCES = IBLOX_VARS['instances']

    for virtual_machine in range(1, int(INSTANCES) + 1):
        inst = "_{}".format(virtual_machine)
        ipv4_address = IBLOX_VARS[inst]['ipv4_address']
        ipv6_address = IBLOX_VARS[inst]['ipv6_address']
        host_name = IBLOX_VARS[inst]['hostname']

    if ARGS.destroy:
        Iblox(host_name, ipv4_address, ipv6_address).destroy()
        terraform_run('destroy')
    else:
        Iblox(host_name, ipv4_address, ipv6_address).rebuild()
        terraform_run('apply')

    byebye()
