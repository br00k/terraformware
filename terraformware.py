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
    - add progress and output to terraform execution
"""
import os
import ast
import json
import argparse
import ConfigParser
from datetime import datetime
import hcl
from jinja2 import Template
from python_terraform import Terraform
from infoblox_client import connector
from infoblox_client import objects
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

MODULE_DIR = os.path.basename(os.getcwd())
CRED_CONF = os.path.join(os.environ['HOME'], '.terraformware.conf')
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
    """ parse arguments """

    parser = argparse.ArgumentParser()
    parser.add_argument('-var-file', dest='vfile', help='process extra var file',
                        action='append', default=[])
    parser.add_argument('-t', '--test', help='only test', action='store_true')
    parser.add_argument('-s', '--showvars', help='show variables', action='store_true')
    parser.add_argument('--init', help='run terraform init', action='store_true')
    parser.add_argument('--destroy', help='destroy resources', action='store_true')
    parser.add_argument('-p', '--plan', help='dry run execution', action='store_true')
    parser.add_argument('-a', '--apply', help='run terraform', action='store_true')

    return parser.parse_args()


def byebye(status=0):
    """ remove main.tf and say good bye """

    if os.access('./main.tf', os.W_OK):
        os.remove('./main.tf')
    os.sys.exit(status)


def load_variables(filenames, terrafile='./variables.tf'):
    """ load terraform variables """

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
    """ render jinja templates """

    config = ConfigParser.RawConfigParser()
    config.readfp(open(CRED_CONF))

    def custom_dictionary(arg_key, arg_sub_key):
        """ return dict value """
        return j2_context[arg_key][arg_sub_key].split('.')[0]

    def custom_variable(arg_var):
        """ return variable """
        return config.get('terraformware', arg_var)

    def custom_global(args_global):
        """ return variable defined in the script """
        return globals()[args_global]

    with open(j2_template, 'r') as my_template:
        template = my_template.read()
    jinja_template = Template(template)
    jinja_template.globals['custom_dictionary'] = custom_dictionary
    jinja_template.globals['custom_variable'] = custom_variable
    jinja_template.globals['custom_global'] = custom_global

    return jinja_template.render(**j2_context)


def terraform_run(action, work_dir='.'):
    """ run terraform """

    tform = Terraform(working_dir=work_dir)
    if action == 'destroy':
        print "running terraform destroy..."
        out = tform.destroy()
    elif action == 'apply':
        print "running terraform plan first..."
        out = tform.cmd('plan')
        print out[1]
        print "applying plan... (takes a while)"
        out = tform.apply(refresh=True)
    elif action == 'init':
        print "running terraform init..."
        out = tform.cmd('init')
    elif action == 'plan':
        print "running terraform init..."
        out = tform.cmd('plan')
        # out = tform.plan()

    print out[1]


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
        """ query for host record: return None if it does not exist """
        try:
            host_rec = self.conn.get_object('record:host', {'name': self.record})[0]
        except TypeError:
            return None
        else:
            return host_rec

    def query_a(self):
        """ query for A record: return None if it does not exist or
            if self.ipv4 matches the existing one """
        try:
            a_rec = self.conn.get_object('record:a', {'name': self.record})[0]
        except TypeError:
            return None
        else:
            if self.ipv4 == str(a_rec['ipv4addr']):
                return 'already_there'
            else:
                return a_rec

    def query_aaaa(self):
        """ query for AAAA record: return None if it does not exist or
            if self.ipv6 matches the existing one """
        try:
            aaaa_rec = self.conn.get_object('record:aaaa', {'name': self.record})[0]
        except TypeError:
            return None
        else:
            if self.ipv6 == str(aaaa_rec['ipv6addr']):
                return 'already_there'
            else:
                return aaaa_rec

    def destroy(self):
        """ clean up host entries """
        host_entry = self.query_host()
        if host_entry:
            self.conn.delete_object(host_entry['_ref'])
            print "destroyed host record {}".format(self.record)

        try:
            self.conn.delete_object(self.conn.get_object('record:a', {'name': self.record})[0]['_ref'])
        except TypeError:
            pass
        else:
            print "destroyed A Record {} with IP {}".format(self.record, self.ipv4)

        try:
            self.conn.delete_object(
                self.conn.get_object('record:aaaa', {'name': self.record})[0]['_ref'])
        except TypeError:
            pass
        else:
            print "destroyed AAAA Record {} with IP {}".format(self.record, self.ipv6)

    def destroy_conditional(self):
        """ clean up host entries """
        host_entry = self.query_host()
        a_entry = self.query_a()
        aaaa_entry = self.query_aaaa()

        if host_entry:
            self.conn.delete_object(host_entry['_ref'])
            print "destroyed host record {}".format(self.record)
        if a_entry and a_entry != 'already_there':
            self.conn.delete_object(a_entry['_ref'])
            print "destroyed A Record {} with IP {}".format(
                self.record, self.ipv4)
        if aaaa_entry and aaaa_entry != 'already_there':
            self.conn.delete_object(aaaa_entry['_ref'])
            print "destroyed AAAA record {} with IPv6 {}".format(
                self.record, self.ipv6)

    def rebuild(self):
        """ - destroy host record (always)
            - destroy A and AAA records only if they don't match
            - create new A and AAA records
        """

        self.destroy_conditional()
        a_entry = self.query_a()
        aaaa_entry = self.query_aaaa()

        if a_entry != 'already_there':
            try:
                objects.ARecord.create(self.conn, view='External',
                                       name=self.record, ip=self.ipv4)
            except Exception as err:
                print "couldn't create A Record for {} with IP {}: {}".format(self.record, self.ipv4, err)
                byebye(1)
            else:
                print "created A Record {} with IP {}".format(
                    self.record, self.ipv4)
        else:
            print "A Record {} with IPv4 {} was already there".format(
                self.record, self.ipv4)

        if aaaa_entry != 'already_there':
            try:
                objects.AAAARecord.create(self.conn, view='External',
                                          name=self.record, ip=self.ipv6)
            except Exception as err:
                print "couldn't create AAAA Record {} with IPv6 {}: {}".format(self.record, self.ipv6, err)
                byebye(1)
            else:
                print "created AAAA Record {} with IP {}".format(
                    self.record, self.ipv6)
        else:
            print "AAAA Record {} with IPv6 {} was already there".format(self.record, self.ipv6)

        print '='*80


if __name__ == '__main__':
    print '='*80
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    START_TIME = datetime.now()
    TEMPLATE = './terraformware.j2'
    RENDERED_FNAME = 'main.tf'

    if not os.access(CRED_CONF, os.W_OK):
        CRED_FILE = open(CRED_CONF, 'w+')
        CRED_FILE.write(CRED_FILE_CONTENT)
        CRED_FILE.close()
        print "\nThe following file has been created: {0}\n".format(CRED_CONF)
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
        else:
            Iblox(host_name, ipv4_address, ipv6_address).rebuild()

    if ARGS.destroy:
        terraform_run('destroy')
    elif ARGS.init:
        terraform_run('init')
    elif ARGS.plan:
        terraform_run('plan')
    elif ARGS.apply:
        terraform_run('apply')

    SPENT = (datetime.now() - START_TIME).seconds
    print "======== Script processed in {} seconds ========\n".format(SPENT)
    byebye()
