#!/usr/bin/env python3

#     2019 Stefan Kauerauf <mail@stefankauerauf.de>
#     last modified: 2/5/2019
#
#     easysmart_datasource.py is part of check_tp-link_easysmart
#     check_tp-link_easysmart is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     check_tp-link_easysmart is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with check_tp-link_easysmart.  If not, see <http://www.gnu.org/licenses/>.
import re
import sys
import logging

import requests

log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
log.addHandler(logging.StreamHandler())
log.debug('Log initialized...')

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

opt_host = None
opt_user = None
opt_pass = None


class DatasourcePlugin():

    def __init__(self, username, password, hostaddress):
        self.username = username
        self.password = password
        self.hostaddress = hostaddress
        self.session = requests.Session()

    def login(self):
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
                sys.exit(1)
        except ConnectionError:
            print('UNKNOWN: connection error during login, check host address')
            sys.exit(1)

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
        except ConnectionError:
            print('UNKNOWN: connection error, check host address')
            sys.exit(1)
        except Exception:
            print('UNKNOWN')
            sys.exit(1)
        return result.text

    def get_all(self):
        # <<<port_statistics>>>
        self.login()
        statistics_body = self.make_request('PortStatisticsRpm.htm')
        port_states = [int(i) for i in re.search('state\:\[(.*)\]\,\n', statistics_body).group(1).split(',')]
        del port_states[-2:]
        port_links = [int(i) for i in re.search('link_status\:\[(.*)\]\,\n', statistics_body).group(1).split(',')]
        del port_links[-2:]
        port_statistics = [int(i) for i in re.search('pkts\:\[(.*)\]\n', statistics_body).group(1).split(',')]
        del port_statistics[-2:]
        port_statistics = [port_statistics[i:i + 4] for i in range(0, len(port_statistics), 4)]
        statistics = []
        for i in range(len(port_states)):
            statistics.append({
                'port': i + 1,
                'state': port_states[i],
                'link': port_links[i],
                'tx_ok': port_statistics[i][0],
                'tx_err': port_statistics[i][1],
                'rx_ok': port_statistics[i][2],
                'rx_err': port_statistics[i][3],
            })
        log.debug(statistics)

        # FORMAT: PORT STATE STATE_NAME LINK LINK_NAME TX_OK TX_ERR RX_OK RX_ERR
        print("<<<ports>>>")
        for i in statistics:
            print(
                "%s %s %s %s %s %s %s %s %s" % (
                i['port'], i['state'], PORT_STATES[i['state']].replace(' ', '_'), i['link'],
                LINK_STATES[i['link']].replace(' ', '_'), i['tx_ok'], i['tx_err'], i['rx_ok'], i['rx_err']))

            self.logout()


def main():
    try:
        usern = sys.argv[2]
        passw = sys.argv[3]
        host = sys.argv[1]
    except IndexError:
        print("Usage: easysmart_datasource.py HOST USER PASSWORD")
        sys.exit(1)

    p = DatasourcePlugin(usern, passw, host)
    p.get_all()


if __name__ == "__main__":
    main()
    sys.exit(0)
