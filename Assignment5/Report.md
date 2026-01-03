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
