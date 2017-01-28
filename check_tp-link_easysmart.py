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
import re

CHECK_MODES = [
    'overview',
    'errors',
]

NAGIOS_STATS = {
    0: 'OK',
    1: 'WARNING',
    2: 'CRITICAL',
    3: 'UNKNOWN',
}

PORT_STATES = {
    0: 'disabled',
    1: 'enabled',
}

LINK_STATES = {
    0: 'down',
    1: 'unknown',
    2: '10MBit Half Duplex',
    3: '10MBit Full Duplex',
    4: '100MBit Half Duplex',
    5: '100MBit Full Duplex',
    6: '1000MBit Full Duplex',
}




class Plugin():

    def __init__(self, hostaddress, username, password, mode, html, ports, warning, critical):
        self.hostaddress = hostaddress
        self.username = username
        self.password = password
        self.mode = mode
        self.html = html
        self.ports = ports
        self.warning = warning
        self.critical = critical
        self.statistics = self.get_statistics()


    def check(self):
        return getattr(self, 'check_%s' % self.mode)()

    def check_errors(self):
        text = ''
        perf = ''
        for port in self.statistics:
            overall_status = 0
            if self.ports == 'all' or str(port['port']) in self.ports:
                port_nagios_status = 0
                if port['tx_err'] > self.warning or port['rx_err'] > self.warning:
                    port_nagios_status = 1
                if port['tx_err'] > self.critical or port['rx_err'] > self.critical:
                    port_nagios_status = 2
                if overall_status < port_nagios_status:
                    overall_status = port_nagios_status
                text += 'port %d %s (%s) TX OK: %d TX ERR: %d RX OK: %d RX ERR: %d (%s)' % (port['port'],
                                                       port['state'],
                                                       port['link'],
                                                       port['tx_ok'],
                                                       port['tx_err'],
                                                       port['rx_ok'],
                                                       port['rx_err'],
                                                       NAGIOS_STATS[port_nagios_status]
                                                       )
                if self.html:
                    text += '</br>'
                else:
                    text += '\n'
                for element in ['tx_ok', 'tx_err', 'rx_ok', 'rx_err']:
                    perf += 'port_%s_%s=%d ' % (port['port'], element, port[element])
        text = text.strip('\n')
        perf = perf.strip(' ')
        return overall_status, text, perf

    def check_overview(self):
        text = ''
        perf = ''
        for port in self.statistics:
            if self.ports == 'all' or str(port['port']) in self.ports:
                text += 'port %d %s (%s) TX OK: %d TX ERR: %d RX OK: %d RX ERR: %d' % (port['port'],
                                                       port['state'],
                                                       port['link'],
                                                       port['tx_ok'],
                                                       port['tx_err'],
                                                       port['rx_ok'],
                                                       port['rx_err']
                                                       )
                if self.html:
                    text += '</br>'
                else:
                    text += '\n'
                for element in ['tx_ok', 'tx_err', 'rx_ok', 'rx_err']:
                    perf += 'port_%s_%s=%d ' % (port['port'], element, port[element])
        text = text.strip('\n')
        perf = perf.strip(' ')
        return 0, text, perf

    def get_statistics(self):
        self.login()
        statistics_body = self.make_request('PortStatisticsRpm.htm')
        port_states = [int(i) for i in re.search('state\:\[(.*)\]\,\n', statistics_body).group(1).split(',')]
        del port_states[-2:]
        port_links = [int(i) for i in re.search('link_status\:\[(.*)\]\,\n', statistics_body).group(1).split(',')]
        del port_links[-2:]
        port_statistics = [int(i) for i in re.search('pkts\:\[(.*)\]\n', statistics_body).group(1).split(',')]
        del port_statistics[-2:]
        port_statistics = [port_statistics[i:i+4] for i in range(0, len(port_statistics), 4)]
        statistics = []
        for i in range(len(port_states)):
            statistics.append({
                'port': i + 1,
                'state': PORT_STATES[port_states[i]],
                'link': LINK_STATES[port_links[i]],
                'tx_ok': port_statistics[i][0],
                'tx_err': port_statistics[i][1],
                'rx_ok': port_statistics[i][2],
                'rx_err': port_statistics[i][3],
            })
        self.logout()
        return statistics

    def login(self):
        self.session = requests.Session()
        login_payload = {
            'username': self.username,
            'password': self.password,
            'logon': 'Login',
        }
        try:
            self.session.post('http://%s/logon.cgi' % self.hostaddress, data=login_payload)
            check_login_response = self.session.get('http://%s/' % self.hostaddress)
            if int(check_login_response.status_code) != 200:
                print('UNKNOWN: login incorrect, check username and password')
                sys.exit(3)
        except ConnectionError as e:
            print('UNKNOWN: connection error during login, check host address')
            sys.exit(3)

    def logout(self):
        self.session.get('http://%s/Logout.htm' % self.hostaddress)

    def make_request(self, target=None):
        url = 'http://%s' % self.hostaddress
        if target:
            url += '/%s' % target

        try:
            result = self.session.get(url)
            if int(result.status_code) != 200:
                raise Exception('unknown error, check compatibility list')
        except ConnectionError as e:
            print('UNKNOW: connection error, check host address')
            sys.exit(3)
        except Exception as e:
            print('UNKNOWN: %s' % e.message)
            sys.exit(3)
        return result.text

def main():
    '''main function configures baseic stuff, parse and check arguments and initializes check'''
    argp = argparse.ArgumentParser()
    argp.add_argument('-H', '--hostaddress', help='the ip address or hostname of the switch')
    argp.add_argument('-U', '--username', help='the username of the administrative web gui user')
    argp.add_argument('-P', '--password', help='the password of the administrative web gui user')
    argp.add_argument('-M', '--mode', help='check mode, available modes are: %s' % ', '.join(CHECK_MODES))
    argp.add_argument('--html', default=False, action='store_true', help='enable html formatted output')
    argp.add_argument('-p', '--ports', default='all', help='comma separated list of ports to check')
    argp.add_argument('-w', '--warning', default='10', help='send and receive warning error count since last check')
    argp.add_argument('-c', '--critical', default='20', help='send and receive critical error count since last check')
    args = argp.parse_args()

    if args.mode not in CHECK_MODES:
        print('UNKNOWN: check mode has to be one of: %s' % ' '.join(CHECK_MODES))
        sys.exit(3)

    try:
        int(args.warning)
        int(args.critical)
    except ValueError:
        print('UNKNOWN: warning and critical thresholds have to be numbers')
        sys.exit(3)


    if args.ports != 'all':
        if not re.match('^(\d+\,{1})*\d+$', args.ports):
            print('UNKNOWN: ports must be given as comma separated list')
            sys.exit(3)

    plugin = Plugin(hostaddress=args.hostaddress, username=args.username,
                    password=args.password, mode=args.mode, html=args.html, ports=args.ports,
                    warning=args.warning, critical=args.critical)
    result_code, result_text, result_perfdata = plugin.check()
    print('%s: %s|%s' % (NAGIOS_STATS[result_code], result_text, result_perfdata))
    sys.exit(result_code)

if __name__ == '__main__':
    main()