from mininet.topo import Topo

class CustomTopo(Topo):
    "Simple Data Center Topology"

    "linkopts - (1:core, 2:aggregation, 3: edge) parameters"
    "fanout - number of child switch per parent switch"
    def __init__(self, linkopts1, linkopts2, linkopts3, fanout=2, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        
        # Add your logic here ...

        
                    
def perfTest():
	"Create network and run simple performance test"
	linkopts1 = {'bw':1000, 'delay':'1ms', 'loss':0.1, 'max_queue_size':1000, 'use_htb':True}
	linkopts2 = {'bw':100, 'delay':'10ms', 'loss':0.1, 'max_queue_size':1000, 'use_htb':True}
	linkopts3 = {'bw':10, 'delay':'10ms', 'loss':0.2, 'max_queue_size':1000, 'use_htb':True}
	topo = CustomTopo(linkopts1,linkopts2,linkopts3,fanout=3)
	net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
	net.start()
	print "Dumping host connections"
	dumpNodeConnections(net.hosts)
	print "Testing network connectivity"
	net.pingAll()
	print "Testing bandwidth between h1 and h2"
	h1, h2 = net.get('h1', 'h2')
	net.iperf((h1, h2))
	print "Testing bandwidth between h1 and h2"
	h1, h2 = net.get('h1', 'h4')
	net.iperf((h1, h4))	
	print "Testing bandwidth between h1 and h6"
	h1, h6 = net.get('h1', 'h6')
	net.iperf((h1, h6))
	net.stop()


if __name__ == '__main__':
   setLogLevel('info')
   perfTest()
