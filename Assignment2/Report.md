# Future Internet Assignment 2
## Testing out POX
command: mininet@mininet-vm:~/pox$ python pox.py log.level --DEBUG Assignment-2.of_sw_tutorial

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
Handy dandy
```bash
sudo mn -c
sudo pkill -f controller
sudo pkill -f pox
```

Run it
```bash
python pox.py log.level --DEBUG forwarding.l2_learning Assignment-2.Skeleton-Lab-2
```