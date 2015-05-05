# Copyright 2015 Cisco Systems, Inc.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import struct

from ipaddr import IPv4Address

from openbgp.message.attribute import Attribute
from openbgp.message.attribute import AttributeID
from openbgp.message.attribute import AttributeFlag
from openbgp.common import constants as bgp_cons
from openbgp.common import exception as excep


class ClusterList(Attribute):
    """
        CLUSTER_LIST is a new, optional, non-transitive BGP attribute of Type
    code 10. It is a sequence of CLUSTER_ID values representing the
    reflection path that the route has passed.
    When an RR reflects a route, it MUST prepend the local CLUSTER_ID to
    the CLUSTER_LIST. If the CLUSTER_LIST is empty, it MUST create a new
    one. Using this attribute an RR can identify if the routing
    information has looped back to the same cluster due to
    misconfiguration. If the local CLUSTER_ID is found in the
    CLUSTER_LIST, the advertisement received SHOULD be ignored.
    (RFC 4456 Page 7)
    """

    ID = AttributeID.CLUSTER_LIST
    FLAG = AttributeFlag.OPTIONAL
    MULTIPLE = False

    @staticmethod
    def parse(value):

        """
        Parse culster list
        :param value
        """
        cluster_list = []
        if len(value) % 4 != 0:
            raise excep.UpdateMessageError(
                sub_error=bgp_cons.ERR_MSG_UPDATE_ATTR_LEN,
                data=repr(value))
        try:
            while value:
                cluster_list.append(IPv4Address(struct.unpack('!I', value[0:4])[0]).__str__())
                value = value[4:]
        except Exception:
            raise excep.UpdateMessageError(
                sub_error=bgp_cons.ERR_MSG_UPDATE_ATTR_LEN,
                data=repr(value))
        return cluster_list

    def construct(self, value, flags=None):

        """
        construct a CLUSTER_LIST path attribute
        :param value:
        :param flags:
        """
        cluster_raw = ''
        if not flags:
            flags = self.FLAG
        try:
            for cluster in value:
                cluster_raw += IPv4Address(cluster).packed
            return struct.pack("!B", flags) + struct.pack('!B', self.ID) \
                + struct.pack("!B", len(cluster_raw)) + cluster_raw
        except Exception:
            raise excep.UpdateMessageError(
                sub_error=bgp_cons.ERR_MSG_UPDATE_ATTR_LEN,
                data=struct.pack('B', flags))
