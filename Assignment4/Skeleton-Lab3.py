from pox.core import core
from collections import defaultdict

import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery
import pox.openflow.spanning_tree

from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.lib.util import dpidToStr

from pox.lib.addresses import IPAddr, EthAddr
from collections import namedtuple
import os


log = core.getLogger()

class CustomSlice (EventMixin):
    def __init__ (self):
        self.listenTo(core.openflow)
        core.openflow_discovery.addListeners(self)

        # Adjacency map.  [sw1][sw2] -> port from sw1 to sw2
        self.adjacency = defaultdict(lambda:defaultdict(lambda:None))

        '''
        We suggest an structure that relates origin-destination MAC address and port:
        (dpid, origin MAC, destination MAC, port : following dpid)
        The structure of self.portmap is a four-tuple key and a string value.
        The type is:
        (dpid string, src MAC addr, dst MAC addr, port (int)) -> dpid of next switch
        '''

        # DPIDs
        D1 = '00-00-00-00-00-01'
        D2 = '00-00-00-00-00-02'
        D3 = '00-00-00-00-00-03'
        D4 = '00-00-00-00-00-04'
        D5 = '00-00-00-00-00-05'
        D6 = '00-00-00-00-00-06'
        D7 = '00-00-00-00-00-07'

        # MACs
        MAC1 = EthAddr('00:00:00:00:00:01')
        MAC2 = EthAddr('00:00:00:00:00:02')
        MAC3 = EthAddr('00:00:00:00:00:03')
        MAC4 = EthAddr('00:00:00:00:00:04')
        MAC5 = EthAddr('00:00:00:00:00:05') # VIDEO
        MAC6 = EthAddr('00:00:00:00:00:06') # HTTP


        # If a packet is at switch X, coming from host A, going to host/server B, and it arrived on port P,
        # then the next switch along the correct path is Y

        self.portmap = {
            # Please add your logic here

            # --- Connection between H1 and Video (200) ---
            # Path: S1 -> S4 -> S7
            (D1, MAC1, MAC5, 200): D4,
            (D4, MAC1, MAC5, 200): D7,
            (D7, MAC1, MAC5, 200): None,
            # Path: S7 -> S4 -> S1
            (D7, MAC5, MAC1, 200): D4,
            (D4, MAC5, MAC1, 200): D1,
            (D1, MAC5, MAC1, 200): None,

            # --- Connection between H1 and HTTP (80) --- (SPECIAL CASE!)
            # Path: S1 -> S2 -> S5 -> S7
            (D1, MAC1, MAC6, 80): D2,
            (D2, MAC1, MAC6, 80): D5,
            (D5, MAC1, MAC6, 80): D7,
            (D7, MAC1, MAC6, 80): None,
            # Path: S7 -> S5 -> S2 -> S1
            (D7, MAC6, MAC1, 80): D5,
            (D5, MAC6, MAC1, 80): D2,
            (D2, MAC6, MAC1, 80): D1,
            (D1, MAC6, MAC1, 80): None,

            # --- Connection between H2 and HTTP (80) ---
            # Path: S2 -> S5 -> S7
            (D2, MAC2, MAC6, 80): D5,
            (D5, MAC2, MAC6, 80): D7,
            (D7, MAC2, MAC6, 80): None,
            # Path: S7 -> S5 -> S2
            (D7, MAC6, MAC2, 80): D5,
            (D5, MAC6, MAC2, 80): D2,
            (D2, MAC6, MAC2, 80): None,

            # --- Connection between H3 and HTTP (80) ---
            # Path: S3 -> S6 -> S7
            (D3, MAC3, MAC6, 80): D6,
            (D6, MAC3, MAC6, 80): D7,
            (D7, MAC3, MAC6, 80): None,
            # Path: S7 -> S5 -> S2
            (D7, MAC6, MAC3, 80): D6,
            (D6, MAC6, MAC3, 80): D3,
            (D3, MAC6, MAC3, 80): None,

            # --- Connection between H4 and Video (200) ---
            # Path: S3 -> S2 -> S1 -> S4 -> S7
            (D3, MAC4, MAC5, 200): D2,
            (D2, MAC4, MAC5, 200): D1,
            (D1, MAC4, MAC5, 200): D4,
            (D4, MAC4, MAC5, 200): D7,
            (D7, MAC4, MAC5, 200): None,
            # Path: S7 -> S4 -> S1 -> S2 -> S3
            (D7, MAC5, MAC4, 200): D4,
            (D4, MAC5, MAC4, 200): D1,
            (D1, MAC5, MAC4, 200): D2,
            (D2, MAC5, MAC4, 200): D3,
            (D3, MAC5, MAC4, 200): None,
        }

    def _handle_ConnectionUp (self, event):
        dpid = dpidToStr(event.dpid)
        log.debug("Switch %s has connected.", dpid)

    def _handle_LinkEvent (self, event):
        l = event.link
        sw1 = dpid_to_str(l.dpid1)
        sw2 = dpid_to_str(l.dpid2)
        log.debug ("link %s[%d] <-> %s[%d]",
            sw1, l.port1,
            sw2, l.port2)
        self.adjacency[sw1][sw2] = l.port1
        self.adjacency[sw2][sw1] = l.port2


    def _handle_PacketIn (self, event):
        """
        Handle packet in messages from the switch to implement above algorithm.
        """
        packet = event.parsed
        tcpp = event.parsed.find('tcp')
        udpp = event.parsed.find('udp')
        # tcpp=80

        # flood, but don't install the rule
        def flood (message = None):
            """ Floods the packet """
            msg = of.ofp_packet_out()
            msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
            msg.data = event.ofp
            msg.in_port = event.port
            event.connection.send(msg)

        def install_fwdrule(event,packet,outport):
            msg = of.ofp_flow_mod()
            msg.idle_timeout = 10
            msg.hard_timeout = 30
            msg.match = of.ofp_match.from_packet(packet, event.port)
            msg.actions.append(of.ofp_action_output(port = outport))
            msg.data = event.ofp
            msg.in_port = event.port
            event.connection.send(msg)


        def forward (message = None):
            this_dpid = dpid_to_str(event.dpid)

            if packet.dst.is_multicast:
                flood()
                return
            else:
                log.debug("Got unicast packet for %s at %s (input port %d):",
                          packet.dst, dpid_to_str(event.dpid), event.port)

            try:
                # Add your logic here
                # 1. Determine the application port and protocol
                dst_port = None
                protocol = None

                # Check for VIDEO (port 200 UDP)
                udpp = packet.find('udp')
                if udpp is not None and (udpp.dstport == 200 or udpp.srcport == 200):
                    dst_port = 200
                    protocol = 'UDP'

                # Check for HTTP (port 80 TCP)
                tcpp = packet.find('tcp')
                if tcpp is not None and (tcpp.dstport == 80 or tcpp.srcport == 80):
                    dst_port = 80
                    protocol = 'TCP'

                #TODO idk mannnn

            except AttributeError:
                log.debug("packet type has no transport ports, flooding")

            # flood and install the flow table entry for the flood
            install_fwdrule(event,packet,of.OFPP_FLOOD)

        forward()

def launch():
    # Ejecute spanning tree para evitar problemas con topologías con bucles
    pox.openflow.discovery.launch()
    pox.openflow.spanning_tree.launch()

    core.registerNew(CustomSlice)