from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.log import setLogLevel, info
from time import sleep

def testCircularTopo():
    # --- Match your mn command exactly ---
    net = Mininet(controller=RemoteController,
                  switch=OVSKernelSwitch,
                  autoSetMacs=True)

    # Controller setup (same as --controller=remote,ip=127.0.0.1,port=6633)
    info("*** Adding remote controller\n")
    c0 = net.addController('c0',
                           controller=RemoteController,
                           ip='127.0.0.1',
                           port=6633)

    # Switches (same as --switch ovsk,protocols=OpenFlow10)
    info("*** Adding switches\n")
    s1 = net.addSwitch('s1', protocols='OpenFlow10')
    s2 = net.addSwitch('s2', protocols='OpenFlow10')
    s3 = net.addSwitch('s3', protocols='OpenFlow10')

    info("*** Creating links\n")
    net.addLink(s1, s2)
    net.addLink(s2, s3)
    net.addLink(s3, s1)

    info("*** Adding hosts\n")
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')

    net.addLink(s1, h1)
    net.addLink(s2, h2)
    net.addLink(s3, h3)

    info("*** Starting network\n")
    net.start()

    sleep(10)

    info("*** Testing connectivity\n")
    net.pingAll()

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    testCircularTopo()
