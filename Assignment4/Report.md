# Assignment 4: Network Slicing

In this assignment, we will force hosts to utilize different physical paths to either VIDEO or HTTP with different bandwidths.
We added hardcoded paths to the portmap which we can then use to forward packets when they arrive at a switch to the correct one.

### Stepts to run and test setup:
1. Start 2 VM instances
2. place skeleton.py in pox/pox/misc
3. run `sudo ./pox.py log.level --DEBUG misc.Skeleton-Lab3 forwarding.l2_learning` in pox dir
4. run 'sudo mn --custom Topo.py --topo p3-2 --controller remote,port=6633 --link tc' where topo is located
5. pingall to test everything is connected
6. listen on both h5 and h6: 'h5 iperf -s -p 200 &' and 'h6 iperf -s -p 80 &'
7. test different connections like 'h3 iperf -c h6 -p 80 -t 2 -i 1'


An example run with the output of all paths for the hosts is shown below:
```
mininet>  h1 iperf -c h5 -p 200 -t 2 -i 1
------------------------------------------------------------
Client connecting to 10.0.0.5, TCP port 200
TCP window size:  187 KByte (default)
------------------------------------------------------------
[  3] local 10.0.0.1 port 43690 connected with 10.0.0.5 port 200
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 1.0 sec  11.9 MBytes  99.6 Mbits/sec
[  3]  1.0- 2.0 sec  11.2 MBytes  94.4 Mbits/sec
[  3]  0.0- 2.0 sec  23.1 MBytes  96.1 Mbits/sec
mininet>  h1 iperf -c h6 -p 80 -t 2 -i 1
------------------------------------------------------------
Client connecting to 10.0.0.6, TCP port 80
TCP window size:  144 KByte (default)
------------------------------------------------------------
[  3] local 10.0.0.1 port 49924 connected with 10.0.0.6 port 80
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 1.0 sec  1.38 MBytes  11.5 Mbits/sec
[  3]  1.0- 2.0 sec  1.12 MBytes  9.44 Mbits/sec
[  3]  0.0- 2.1 sec  2.50 MBytes  10.2 Mbits/sec
mininet>  h2 iperf -c h6 -p 80 -t 2 -i 1
------------------------------------------------------------
Client connecting to 10.0.0.6, TCP port 80
TCP window size:  136 KByte (default)
------------------------------------------------------------
[  3] local 10.0.0.2 port 33088 connected with 10.0.0.6 port 80
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 1.0 sec  1.00 MBytes  8.39 Mbits/sec
[  3]  1.0- 2.0 sec   768 KBytes  6.29 Mbits/sec
[  3]  0.0- 2.0 sec  1.75 MBytes  7.19 Mbits/sec
mininet>  h3 iperf -c h6 -p 80 -t 2 -i 1
------------------------------------------------------------
Client connecting to 10.0.0.6, TCP port 80
TCP window size:  136 KByte (default)
------------------------------------------------------------
[  3] local 10.0.0.3 port 36312 connected with 10.0.0.6 port 80
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 1.0 sec  1.38 MBytes  11.5 Mbits/sec
[  3]  1.0- 2.0 sec  1.12 MBytes  9.44 Mbits/sec
[  3]  0.0- 2.1 sec  2.50 MBytes  10.2 Mbits/sec
mininet>  h4 iperf -c h5 -p 200 -t 2 -i 1
------------------------------------------------------------
Client connecting to 10.0.0.5, TCP port 200
TCP window size:  204 KByte (default)
------------------------------------------------------------
[  3] local 10.0.0.4 port 52046 connected with 10.0.0.5 port 200
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 1.0 sec  11.8 MBytes  98.6 Mbits/sec
[  3]  1.0- 2.0 sec  11.2 MBytes  94.4 Mbits/sec
[  3]  0.0- 2.0 sec  23.0 MBytes  95.9 Mbits/sec
mininet> 
```
