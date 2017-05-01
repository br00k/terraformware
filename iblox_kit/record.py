#!/usr/bin/python
#
"""
  Add, modify or delete Infoblox records
"""
import os
import ConfigParser
import ipaddress
from infoblox_client import connector
from infoblox_client import objects
import iblox_kit.config
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

iblox_kit.config.check()


class Iblox(object):
    """manage infoblox entries"""
    config = ConfigParser.RawConfigParser()

    def __init__(self, network, record, ipv4, ipv6=None):
        print '-'*74
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self.network = network
        self.record = record
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.config.readfp(open(iblox_kit.config.CRED_CONF))
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
            already_there if self.ipv4 matches the existing one """
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
            already_there if self.ipv6 matches the existing one """
        try:
            aaaa_rec = self.conn.get_object('record:aaaa', {'name': self.record})[0]
        except TypeError:
            return None
        else:
            if self.ipv6 == str(aaaa_rec['ipv6addr']):
                return 'already_there'
            else:
                return aaaa_rec

    def query_ptr46(self):
        """ query for PTR4 and PTR6 records and return generator """
        ptr_46 = self.conn.get_object('record:ptr', {'ptrdname': self.record})
        for ptr in ptr_46:
            yield ptr

    def destroy(self):
        """ clean up host entries """
        host_entry = self.query_host()
        if host_entry:
            self.conn.delete_object(host_entry['_ref'])
            print "destroyed host record {}".format(self.record)

        try:
            self.conn.delete_object(self.conn.get_object(
                'record:a', {'name': self.record})[0]['_ref'])
        except TypeError:
            pass
        else:
            print "destroyed A Record {}".format(self.record)

        try:
            self.conn.delete_object(self.conn.get_object(
                'record:aaaa', {'name': self.record})[0]['_ref'])
        except TypeError:
            pass
        else:
            print "destroyed AAAA Record {}".format(self.record)

        try:
            ptr46 = list(self.query_ptr46())
        except TypeError:
            pass
        else:
            for ptr in ptr46:
                ptr_rec = str(ptr['_ref']).split(':')[-1].split('/')[0]
                try:
                    self.conn.delete_object(ptr['_ref'])
                except TypeError:
                    pass
                else:
                    print "destroyed PTR Record {} for {}".format(ptr_rec, self.record)

    def destroy_conditional(self):
        """ clean up host entries """
        host_entry = self.query_host()
        a_entry = self.query_a()
        aaaa_entry = self.query_aaaa()
        ucode_ipv4 = self.ipv4.decode('utf-8')
        rev_ipv4 = str(ipaddress.ip_address(ucode_ipv4).reverse_pointer)
        if self.ipv6:
            ucode_ipv6 = self.ipv6.decode('utf-8')
            rev_ipv6 = str(ipaddress.ip_address(ucode_ipv6).reverse_pointer)
        try:
            ptr46_entry = list(self.query_ptr46())
        except TypeError:
            ptr46_entry = []

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
        for ptr in ptr46_entry:
            ptr_rec = str(ptr['_ref']).split(':')[-1].split('/')[0]
            if ptr_rec != rev_ipv4 and ptr_rec != rev_ipv6:
                self.conn.delete_object(ptr['_ref'])
                print "destroyed PTR record {} for {}".format(ptr_rec, self.record)

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
                objects.ARecord.create(self.conn, view=self.network,
                                       update_if_exists=True,
                                       name=self.record, ip=self.ipv4)
            except Exception as err:
                print "couldn't create A Record for {} with IP {}: {}".format(
                    self.record, self.ipv4, err)
                os.sys.exit(1)
            else:
                print "created A Record {} with IP {}".format(
                    self.record, self.ipv4)
        else:
            print "A Record {} with IPv4 {} is already there".format(
                self.record, self.ipv4)

        if self.ipv6:
            if aaaa_entry != 'already_there':
                try:
                    objects.AAAARecord.create(self.conn, view=self.network,
                                              name=self.record, ip=self.ipv6)
                except Exception as err:
                    print "couldn't create AAAA Record {} with IPv6 {}: {}".format(
                        self.record, self.ipv6, err)
                    os.sys.exit(1)
                else:
                    print "created AAAA Record {} with IP {}".format(
                        self.record, self.ipv6)
            else:
                print "AAAA Record {} with IPv6 {} is already there".format(
                    self.record, self.ipv6)

            try:
                objects.PtrRecordV6.create(self.conn, view=self.network,
                                           update_if_exists=True, ip=self.ipv6,
                                           ptrdname=self.record)
            except Exception as err:
                print "couldn't create PTR v6 Record {} for host {}: {}".format(
                    self.ipv6, self.record, err)
                os.sys.exit(1)
            else:
                print "created/updated PTR v6 Record {} for host {}".format(
                    self.ipv6, self.record)
        else:
            print "skipping AAAA Record\nskipping PRT v6 Record"

        try:
            objects.PtrRecordV4.create(self.conn, view=self.network,
                                       update_if_exists=True, ip=self.ipv4,
                                       ptrdname=self.record)
        except Exception as err:
            print "couldn't create PTR Record {} for host {}: {}".format(
                self.ipv4, self.record, err)
            os.sys.exit(1)
        else:
            print "created/updated PTR Record {} for host {}".format(
                self.ipv4, self.record)

        print '-'*74
