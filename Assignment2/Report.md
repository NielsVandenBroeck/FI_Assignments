 # Future Internet Assignment 2
## Testing out POX
```bash
mininet@mininet-vm:~/pox$ python pox.py log.level --DEBUG Assignment-2.of_sw_tutorial
```

- Dumb HUB:
    - h1: all messages
- Pair HUB:
  - h1: only ARP requests
- Lazy HUB
  - h1: all messages

- Bad Switch:
  - h1: ARP where is 2, msg 3->2, ARP reply location of 3 
- Pair Switch:
  - h1: only ARP where 2 twice
  - => 100% packet loss
- Ideal Pair Switch:
  - h1: only ARP where 2 twice

## Firewall
Commands before running the firewall and topology:
```bash
sudo mn -c
sudo pkill -f controller
sudo pkill -f pox

sudo lsof -i :6633
sudo kill -9 (PID)
```

Running the firewall
```bash
python pox.py log.level --DEBUG forwarding.l2_learning Assignment-2.Skeleton-Lab-2
```

Add openflow.discovery and openflow.spanning_tree arguments for circular topologies:
```bash
python pox.py openflow.discovery openflow.spanning_tree log.level --DEBUG forwarding.l2_learning Assignment-2.Skeleton-Lab-2
```



## Example topologies and their pingall traces


When doing Pingall, it will send all possible packets from each host to another. We can easily check which connections fail when a X appears, otherwise, the name of the host is shown.

### Single:
```
mininet@mininet-vm:~$ sudo -E mn --topo single,3 --mac   --switch ovsk,protocols=OpenFlow10   --controller=remote,ip=127.0.0.1,port=6633
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 
*** Adding switches:
s1 
*** Adding links:
(h1, s1) (h2, s1) (h3, s1) 
*** Configuring hosts
h1 h2 h3 
*** Starting controller
c0 
*** Starting 1 switches
s1 ...
*** Starting CLI:
```

```
mininet> pingall
*** Ping: testing ping reachability
h1 -> h2 h3 
h2 -> h1 X 
h3 -> h1 X 
*** Results: 33% dropped (4/6 received)
```



### Tree (3,2):
```
mininet@mininet-vm:~$ sudo -E mn --topo tree,3,2 --mac   --switch ovsk,protocols=OpenFlow10   --controller=remote,ip=127.0.0.1,port=6633
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 h5 h6 h7 h8 
*** Adding switches:
s1 s2 s3 s4 s5 s6 s7 
*** Adding links:
(s1, s2) (s1, s5) (s2, s3) (s2, s4) (s3, h1) (s3, h2) (s4, h3) (s4, h4) (s5, s6) (s5, s7) (s6, h5) (s6, h6) (s7, h7) (s7, h8) 
*** Configuring hosts
h1 h2 h3 h4 h5 h6 h7 h8 
*** Starting controller
c0 
*** Starting 7 switches
s1 s2 s3 s4 s5 s6 s7 ...
*** Starting CLI:
```
```
mininet> pingall
*** Ping: testing ping reachability
h1 -> h2 h3 X h5 h6 h7 h8 
h2 -> h1 X h4 h5 h6 h7 h8 
h3 -> h1 X h4 h5 h6 X h8 
h4 -> X h2 h3 h5 h6 h7 h8 
h5 -> h1 h2 h3 h4 X h7 h8 
h6 -> h1 h2 h3 h4 X h7 h8 
h7 -> h1 h2 X h4 h5 h6 h8 
h8 -> h1 h2 h3 h4 h5 h6 h7 
*** Results: 14% dropped (48/56 received)
```

### Circular:
For this type of topology, we created a python file where three switches are connected to each other in a circular shape. Each switch has a host connected to it.
The output looks slightly different from the other examples since we ran it through a python file.

To make this topology work without the packets to circulate infinitely, we added openflow.discovery and openflow.spanning_tree to make pox transform the topology into a tree.

```
mininet@mininet-vm:~$ sudo python3 Assignments/circular_topology.py 
*** Adding remote controller
*** Adding switches
*** Creating links
*** Adding hosts
*** Starting network
*** Configuring hosts
h1 h2 h3 
*** Starting controller
c0 
*** Starting 3 switches
s1 s2 s3 ...
*** Testing connectivity
*** Ping: testing ping reachability
h1 -> h2 h3 
h2 -> h1 X 
h3 -> h1 X 
*** Results: 33% dropped (4/6 received)
*** Stopping 1 controllers
c0 
*** Stopping 6 links
......
*** Stopping 3 switches
s1 s2 s3 
*** Stopping 3 hosts
h1 h2 h3 
*** Done
```

