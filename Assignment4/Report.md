1. Start 2 VM instances
2. place skeleton.py in pox/pox/misc
3. run 'sudo ./pox.py log.level --DEBUG misc.Skeleton-Lab3 forwarding.l2_learning' in pox dir
4. run 'sudo mn --custom Topo.py --topo p3-2 --controller remote,port=6633 --link tc' where topo is located
5. pingall to test everything is connected
6. listen on both h5 and h6: 'h5 iperf -s -p 200 &' and 'h6 iperf -s -p 80 &'
7. test different connections like 'h3 iperf -c h6 -p 80 -t 2 -i 1'
