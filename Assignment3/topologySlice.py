'''
Coursera:
- Software Defined Networking (SDN) course
-- Network Virtualization

Professor: Nick Feamster
Teaching Assistant: Arpit Gupta
'''

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

VLAN_HIGH = 100
VLAN_LOW = 10

class TopologySlice (EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)
        log.debug("Enabling Slicing Module")

    def _install_flow(self, connection, priority, match, actions):
        fm = of.ofp_flow_mod()
        fm.priority = priority
        fm.match = match
        fm.actions = actions
        connection.send(fm)

    """This event will be raised each time a switch will connect to the controller"""
    def _handle_ConnectionUp(self, event):

        # Use dpid to differentiate between switches (datapath-id)
        # Each switch has its own flow table. As we'll see in this
        # example we need to write different rules in different tables.
        dpid = dpidToStr(event.dpid)
        connection = event.connection
        log.info("Configuring Switch %s", dpid)

        # --- s1 ---
        if dpid == '00-00-00-00-00-01':
            # h1, add VLAN 100 -> s2
            match = of.ofp_match(in_port=3)
            actions = [
                of.ofp_action_vlan_vid(vlan_vid=VLAN_HIGH),
                of.ofp_action_output(port=1)
            ]
            self._install_flow(connection, 10, match, actions)

            # h2, add VLAN 10 -> s4
            match = of.ofp_match(in_port=4)
            actions = [
                of.ofp_action_vlan_vid(vlan_vid=VLAN_LOW),
                of.ofp_action_output(port=2)
            ]
            self._install_flow(connection, 10, match, actions)

            # s2, strip VLAN 100
            match = of.ofp_match(in_port=1, dl_vlan=VLAN_HIGH)
            actions = [
                of.ofp_action_strip_vlan(),
                of.ofp_action_output(port=3)
            ]
            self._install_flow(connection, 20, match, actions)

            # s4, strip VLAN 10
            match = of.ofp_match(in_port=2, dl_vlan=VLAN_LOW)
            actions = [
                of.ofp_action_strip_vlan(),
                of.ofp_action_output(port=4)
            ]
            self._install_flow(connection, 20, match, actions)

        # --- s2 ---
        elif dpid == '00-00-00-00-00-02':

            # s1 -> s3
            match = of.ofp_match(in_port=1, dl_vlan=VLAN_HIGH)
            actions = [of.ofp_action_output(port=2)]
            self._install_flow(connection, 10, match, actions)

            # s3 -> s1
            match = of.ofp_match(in_port=2, dl_vlan=VLAN_HIGH)
            actions = [of.ofp_action_output(port=1)]
            self._install_flow(connection, 10, match, actions)

        # --- s3 ---
        elif dpid == '00-00-00-00-00-03':

            # h3, strip VLAN 100
            match = of.ofp_match(in_port=1, dl_vlan=VLAN_HIGH)
            actions = [
                of.ofp_action_strip_vlan(),
                of.ofp_action_output(port=3)
            ]
            self._install_flow(connection, 20, match, actions)

            # h4, strip VLAN 10
            match = of.ofp_match(in_port=2, dl_vlan=VLAN_LOW)
            actions = [
                of.ofp_action_strip_vlan(),
                of.ofp_action_output(port=4)
            ]
            self._install_flow(connection, 20, match, actions)

            # h3 add VLAN 100 -> s2
            match = of.ofp_match(in_port=3)
            actions = [
                of.ofp_action_vlan_vid(vlan_vid=VLAN_HIGH),
                of.ofp_action_output(port=1)
            ]
            self._install_flow(connection, 10, match, actions)

            # h4 add VLAN 10 -> s3
            match = of.ofp_match(in_port=4)
            actions = [
                of.ofp_action_vlan_vid(vlan_vid=VLAN_LOW),
                of.ofp_action_output(port=2)
            ]
            self._install_flow(connection, 10, match, actions)

        # --- s4 ---
        elif dpid == '00-00-00-00-00-04':

            # s1 -> s3
            match = of.ofp_match(in_port=2, dl_vlan=VLAN_LOW)
            actions = [of.ofp_action_output(port=1)]
            self._install_flow(connection, 10, match, actions)

            # s3 -> s1
            match = of.ofp_match(in_port=1, dl_vlan=VLAN_LOW)
            actions = [of.ofp_action_output(port=2)]
            self._install_flow(connection, 10, match, actions)

        # --- Default Deny (Final Rule on ALL Switches) ---
        # This is a blanket rule to drop any traffic that did not match a higher-priority flow.
        # Priority 1 ensures this is the last rule checked. No actions means the packet is dropped.
        fm = of.ofp_flow_mod(priority=1)
        connection.send(fm)
        log.info("Switch %s: Installed final Default Deny (Drop) rule.", dpid)

def launch():
    # Run spanning tree so that we can deal with topologies with loops
    pox.openflow.discovery.launch()
    pox.openflow.spanning_tree.launch()

    '''
    Starting the Topology Slicing module
    '''
    core.registerNew(TopologySlice)
