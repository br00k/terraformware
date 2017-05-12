#!/usr/bin/python
#
""" check if the configuration file is present
    and create it if it's missing
"""
import os
import platform

if platform.system() == 'Windows':
    CRED_CONF = os.path.join(os.path.expanduser('~'), 'terraformware.cfg')
else:
    CRED_CONF = os.path.join(os.environ['HOME'], '.terraformware.conf')

CRED_FILE_CONTENT = """[terraformware]\n
# Vcenter username (AD user) <string>: your_username
vsphere_username = your_username\n
# Vcenter password (AD password) <string>: your_password
vsphere_password = your_secret_pass_here\n
# VSphere server <string>: vsphere server fqdn
vsphere_server = chvc01.domain.com\n
# Infoblox username <string>: your_username
iblox_username = your_username\n
# Infoblox password <string>: your_password
iblox_password = your_secret_pass_here\n
# Infoblox server <string>: infblox server fqdn
iblox_server = infoblox.domain.com\n
# Consul server:port <string>: consul server fqdn:port
consul_server = consul01.domain.com:8500\n
# Consul access token <string>: consul secret
consul_token = xxxxxxxxxxx\n
"""


def check():
    """ Check config file """
    if not os.access(CRED_CONF, os.W_OK):
        cred_file = open(CRED_CONF, 'w+')
        cred_file.write(CRED_FILE_CONTENT)
        cred_file.close()
        print "\nThe following file has been created: {0}\n".format(CRED_CONF)
        print "Fill it with proper values and run the script again\n"
        os.sys.exit()
