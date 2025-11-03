from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.util import irange, dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSSwitch, OVSBridge, Controller
from mininet.link import TCLink
from mininet.nodelib import LinuxBridge


class CustomTopo(Topo):
    "Simple Data Center Topology"

    "linkopts - (1:core, 2:aggregation, 3: edge) parameters"
    "fanout - number of child switch per parent switch"

    def __init__(self, linkopts1, linkopts2, linkopts3, fanout=2, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)

        # Add your logic here ...
        core = self.addSwitch('s0')
        switch = 1

        aggregations = []
        edges = []
        hosts = []

        for i in range(fanout):
            aggregations.append(self.addSwitch(f's{switch}'))
            switch += 1
            self.addLink(core, aggregations[i], **linkopts1)

        for i in range(len(aggregations)):
            for j in range(fanout):
                edges.append(self.addSwitch(f's{switch}'))
                switch += 1
                self.addLink(aggregations[i], edges[j], **linkopts2)

        for i in range(len(edges)):
            for j in range(fanout):
                hosts.append(self.addHost(f'h{i*fanout+j}'))
                self.addLink(edges[i], hosts[i*fanout+j], **linkopts3)
        print("# hosts: ", len(hosts))


def perfTest():
    "Create network and run simple performance test"
    linkopts1 = {'bw': 1000, 'delay': '1ms', 'loss': 0.1, 'max_queue_size': 1000, 'use_htb': True}
    linkopts2 = {'bw': 100, 'delay': '10ms', 'loss': 0.1, 'max_queue_size': 1000, 'use_htb': True}
    linkopts3 = {'bw': 10, 'delay': '10ms', 'loss': 0.2, 'max_queue_size': 1000, 'use_htb': True}
    topo = CustomTopo(linkopts1, linkopts2, linkopts3, fanout=3)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    print("Dumping host connections")
    dumpNodeConnections(net.hosts)
    print("Testing network connectivity")
    net.pingAll()
    print("Testing bandwidth between h1 and h2")
    h1, h2 = net.get('h1', 'h2')
    net.iperf((h1, h2))
    print("Testing bandwidth between h1 and h2")
    h1, h4 = net.get('h1', 'h4')
    net.iperf((h1, h4))
    print("Testing bandwidth between h1 and h6")
    h1, h6 = net.get('h1', 'h6')
    net.iperf((h1, h6))
    net.stop()


if __name__ == '__main__':
    # setLogLevel('info')
    perfTest()
