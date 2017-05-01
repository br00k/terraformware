#!/usr/bin/python
#
""" check if configuration file is present
    and create it if missing
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


def check():
    """ Check config file """
    if not os.access(CRED_CONF, os.W_OK):
        CRED_FILE = open(CRED_CONF, 'w+')
        CRED_FILE.write(CRED_FILE_CONTENT)
        CRED_FILE.close()
        print "\nThe following file has been created: {0}\n".format(CRED_CONF)
        print "Fill it with proper values and run the script again\n"
        os.sys.exit()
