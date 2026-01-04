table_add IngressPipeImpl.arp_exact arp_reply 10.0.1.2 => 08:00:00:00:00:02
table_add IngressPipeImpl.arp_exact arp_reply 10.0.1.1 => 08:00:00:00:00:01
table_add IngressPipeImpl.arp_exact arp_reply 10.0.1.51 => 08:00:00:00:00:01
table_add IngressPipeImpl.arp_exact arp_reply 10.0.1.52 => 08:00:00:00:00:02
table_add IngressPipeImpl.arp_exact arp_reply 192.168.1.51 => 0a:00:00:00:00:01
table_add IngressPipeImpl.arp_exact arp_reply 192.168.1.52 => 0a:00:00:00:00:02

table_add IngressPipeImpl.ipv4_forward set_egress_port 10.0.1.1 => 1 08:00:00:00:00:01
table_add IngressPipeImpl.ipv4_forward set_egress_port 10.0.1.2 => 2 08:00:00:00:00:02
table_add IngressPipeImpl.ipv4_forward set_egress_port 192.168.1.1 => 3 0a:00:00:00:00:01
table_add IngressPipeImpl.ipv4_forward set_egress_port 192.168.1.2 => 4 0a:00:00:00:00:02

table_add nat nat_destination 08:00:00:00:00:01 10.0.1.51 => 192.168.1.51 192.168.1.1 3 0a:00:00:00:00:01
table_add nat nat_destination 0a:00:00:00:00:01 192.168.1.51 => 10.0.1.51 10.0.1.1 1 08:00:00:00:00:01
table_add nat nat_destination 08:00:00:00:00:02 10.0.1.52 => 192.168.1.52 192.168.1.2 4 0a:00:00:00:00:02
table_add nat nat_destination 0a:00:00:00:00:02 192.168.1.52 => 10.0.1.52 10.0.1.2 2 08:00:00:00:00:02