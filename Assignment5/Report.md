# P4
## Goals
- h1 ping 10.0.1.51
  - translate dest addr -> 192.168.1.1 (h11)
  - translate source addr -> 192.168.1.51
  - echo packet start of with NAT addresses
  - when in switch src and dest will be 'global' addresses (10.0.1.51, 10.0.1.1)
- h2 ping 10.0.1.52
  - translate dest addr -> 192.168.1.2 (h22)
  - translate source addr -> 192.168.1.52
  - echo packet start of with NAT addresses
  - when in switch src and dest will be 'global' addresses (10.0.1.52, 10.0.1.2)

## Running
1. Navigate to tutorials/PA1 in your VM. 
2. Run `make run`
3. Open a new terminal window. 
4. Run `cat rules.sh - | simple_switch_CLI --thrift-port 9090`
5. Go to mininet 
6. Run `ping h1 10.0.1.51 -c 5`
7. Run `ping h2 10.0.1.52 -c 5`
