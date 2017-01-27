#!/usr/bin/env python2

#    check_tp-link_easysmart
#    2017 Stefan Kauerauf <mail@stefankauerauf.de>
#    Plugin for tp-link easysmart switch monitoring.
#    Tested with:
#
#    TP-Link TL-SG108E
#    Hardware version: TL-SG108E 2.0
#    Firmware version: 1.0.1 Build 20160108 Rel.57851
#
#
#    This file is part of check_tp-link_easysmart.
#    check_tp-link_easysmart is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    check_tp-link_easysmart is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with check_tp-link_easysmart.  If not, see <http://www.gnu.org/licenses/>.

import requests
from requests import ConnectionError
from requests.auth import HTTPBasicAuth
import argparse
import sys

CHECK_MODES = [
    'overview',
]

class Plugin():

    def __init__(self, hostaddress, username, password, mode):
        self.hostaddress = hostaddress
        self.username = username
        self.password = password
        self.mode = mode


    def check(self):
        return getattr(self, 'check_%s' % self.mode)()

    def check_overview(self):
        result_body = self.make_request('PortStatisticsRpm.htm')

        return 0, 'text', 'perf'

    def make_request(self, target=None):
        url = 'http://%s' % self.hostaddress
        if target:
            url += '/%s' % target
        with requests.Session() as session:
            #TODO: make fucking login first, but how?
            try:
                result = requests.get(url)
                if int(result.status_code) != 200:
                    raise Exception('unknown error, check compatibility list')
            except ConnectionError:
                print('UNKNOW: connection error, check host address')
                sys.exit(3)
            except Exception as e:
                print('UNKNOWN: %s' % e.message)
                sys.exit(3)
        return result.text

# ConnectionError falsche ip

def main():
    '''main function configures baseic stuff, parse and check arguments and initializes check'''
    argp = argparse.ArgumentParser()
    argp.add_argument('-H', '--hostaddress', help='the ip address or hostname of the switch')
    argp.add_argument('-U', '--username', help='the username of the administrative web gui user')
    argp.add_argument('-P', '--password', help='the password of the administrative web gui user')
    argp.add_argument('-M', '--mode', help='check mode, available modes are: %s' % ', '.join(CHECK_MODES))
    args = argp.parse_args()

    plugin = Plugin(hostaddress=args.hostaddress, username=args.username,
                    password=args.password, mode=args.mode)
    result_code, result_text, result_perfdata = plugin.check()


if __name__ == '__main__':
    main()