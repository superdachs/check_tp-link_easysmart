#     2019 Stefan Kauerauf <mail@stefankauerauf.de>
#     last modified: 2/5/2019
#
#     easysmart.py is part of check_tp-link_easysmart
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


def inventory_easysmart_ports(info):
    print(info)
    return []


def check_easysmart_ports(item, params, info):
    return 3, "Sorry - not implemented"


check_info["easysmart_ports"] = {
    'check_function': check_easysmart_ports,
    'inventory_function': inventory_easysmart_ports,
    'service_description': 'status and statistics of port %s',
    'has_perfdata': False,
}