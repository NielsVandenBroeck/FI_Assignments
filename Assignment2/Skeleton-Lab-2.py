# Part of this code is taken from the SDN coursera course by Prof. Nick Feamster
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os
import csv

# Please add the classes and methods you consider necessary



log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ['HOME']


class Firewall(EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)
        log.debug("Activating Firewall")

        self.blocked = set()
        self._read_firewall_rules()

    def _read_firewall_rules(self):
        try:
            with open("./pox/Assignment-2/firewall-policies.csv", "r") as rules:
                log.info("Reading firewall rules")
                reader = csv.reader(rules, delimiter=',')
                next(reader, None)  # skip header
                for row in reader:
                    _, src, dest = row
                    self.blocked.add((EthAddr(src), EthAddr(dest)))

                    log.info(f"\n\tsrc: {src}, dst: {dest}")
        except IOError as e:
            log.error(f"Failed to read firewall rules: {e}")

    def _handle_ConnectionUp(self, event):
        # Please add your code here
        log.debug("Switch %s connected, installing firewall rules", dpidToStr(event.dpid))

        for (src, dst) in self.blocked:
            msg = of.ofp_flow_mod() # msg to modify flow table
            msg.match.dl_src = src
            msg.match.dl_dst = dst
            msg.actions = [] # can be left out default actions is to drop
            event.connection.send(msg)
            log.debug("Dropped traffic rule installed: %s -> %s", src, dst)
        log.debug("Installed rules in %s", dpidToStr(event.dpid))


def launch():
    core.registerNew(Firewall)
