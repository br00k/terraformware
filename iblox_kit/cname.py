#!/usr/bin/python
#
"""
  Add, modify or delete Infoblox CNAME
"""
import os
import argparse
import textwrap
import platform
import ConfigParser
from infoblox_client import connector
from infoblox_client import objects
import iblox_kit.config
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


iblox_kit.config.check()


class Iblox(object):
    """manage infoblox entries"""
    config = ConfigParser.RawConfigParser()

    def __init__(self, network, record, alias):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self.network = network
        self.record = record
        self.alias = alias
        self.config.readfp(open(iblox_kit.config.CRED_CONF))
        self.opts = {
            'host': self.config.get('terraformware', 'iblox_server'),
            'username': self.config.get('terraformware', 'iblox_username'),
            'password': self.config.get('terraformware', 'iblox_password')
            }
        self.conn = connector.Connector(self.opts)

    def query_alias(self):
        """ query for CNAME record: return None if it does not exist or
            if self.alias matches the existing one """
        try:
            alias_rec = self.conn.get_object('record:cname', {'name': self.alias})[0]
        except TypeError:
            return None
        else:
            if self.record == str(alias_rec['canonical']):
                return 'already_there'
            else:
                return alias_rec

    def destroy(self):
        """ clean up CNAME entry """
        try:
            self.conn.delete_object(self.conn.get_object(
                'record:cname', {'name': self.alias})[0]['_ref'])
        except TypeError:
            print "cound not find CNAME {}".format(self.alias)
        else:
            print "destroyed CNAME {}".format(self.alias)

    def destroy_conditional(self):
        """ clean up host entries """
        alias_entry = self.query_alias()
        if alias_entry and alias_entry != 'already_there':
            self.conn.delete_object(alias_entry['_ref'])
            print "destroyed CNAME record {}".format(self.alias)
            return 'did something'
        elif alias_entry == 'already_there':
            return 'already_there'
        else:
            return None

    def rebuild(self):
        """ - destroy alias record (if it is not matching)
            - create a new alias record if there isn't one already
        """

        try_destroy = self.destroy_conditional()

        if try_destroy == 'already_there':
            print "A CNAME {} associated to {} is already there".format(
                self.alias, self.record)
        else:
            try:
                objects.CNAMERecord.create(self.conn, view=self.network,
                                           name=self.alias, canonical=self.record)
            except Exception as err:
                print "couldn't create CNAME {} to Record {}: {}".format(
                    self.alias, self.record, err)
                os.sys.exit(1)
            else:
                print "created CNAME record {} associated to {}".format(
                    self.alias, self.record)
