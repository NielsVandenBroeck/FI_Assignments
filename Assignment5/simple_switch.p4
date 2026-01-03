#include <core.p4>
#include <v1model.p4>

// Type aliases defined for convenience
typedef bit<9>   port_num_t;
typedef bit<48>  mac_addr_t;
typedef bit<32>  ipv4_addr_t;
typedef bit<16>  l4_port_t;

const bit<16> ETHERTYPE_IPV4 = 0x0800;
const bit<16> ETHERTYPE_ARP = 0x0806;
const bit<8> IPV4_ICMP = (bit<8>)1;
const bit<8> IPV4_TCP=(bit<8>)6;

// ARP RELATED CONST VARS - RFC 822
const bit<16> ARP_HTYPE = 0x0001; //Ethernet Hardware type is 1
const bit<16> ARP_PTYPE = ETHERTYPE_IPV4; //Protocol used for ARP is IPV4
const bit<8>  ARP_HLEN  = 6; //Ethernet address size is 6 bytes
const bit<8>  ARP_PLEN  = 4; //IP address size is 4 bytes
const bit<16> ARP_REQ = 1; //Operation 1 is request
const bit<16> ARP_REPLY = 2; //Operation 2 is reply


//------------------------------------------------------------------------------
// HEADER DEFINITIONS
//------------------------------------------------------------------------------

// Standard IEEE 802.3
header ethernet_t {
	bit<48>  dst_addr;
	mac_addr_t  src_addr;
	bit<16>     ether_type;
}

// Address Resolution Protocol RFC 826
header arp_t {
  bit<16>   h_type;
  bit<16>   p_type;
  bit<8>    h_len;
  bit<8>    p_len;
  bit<16>   op_code;
  mac_addr_t src_mac;
  ipv4_addr_t src_ip;
  mac_addr_t dst_mac;
  ipv4_addr_t dst_ip;
}

//TO-DO: Define the fields of the IPv4 header
//HINT: Refer to RFC791
header ipv4_t {
  bit<4> version;
  bit<4> IHL;
  bit<8> service;
  bit<16> length;
  bit<16> id;
  bit<3> flags;
  bit<13> offset;
  bit<8> ttl;
  bit<8> protocol;
  bit<16> checksum;
  bit<32> srcAddr;
  bit<32> destAddr;
}

struct parsed_headers_t {
    ethernet_t ethernet;
    arp_t arp;
    ipv4_t ipv4;
}

struct local_metadata_t {
        @field_list(1)
        port_num_t ingress_port;
}


//------------------------------------------------------------------------------
// INGRESS PIPELINE
//------------------------------------------------------------------------------

parser ParserImpl (packet_in packet,
                   out parsed_headers_t hdr,
                   inout local_metadata_t local_metadata,
                   inout standard_metadata_t standard_metadata)
{

    // Default entry point of the parser. It just transitions to parse Ethernet Frames
    state start {
        transition select(standard_metadata.ingress_port) {
            default: parseEthernet;
        }
    }

    state parseEthernet {
        packet.extract(hdr.ethernet);

        transition select(hdr.ethernet.ether_type){
	    ETHERTYPE_IPV4: parse_ipv4;
	    ETHERTYPE_ARP: parse_arp;
            default: accept;
        }
    }

    state parse_arp {
        packet.extract(hdr.arp);
        transition select(hdr.arp.op_code) {
                ARP_REQ: accept;
        }
    }


    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            default: accept;
        }
    }

}


control VerifyChecksumImpl(inout parsed_headers_t hdr,
                           inout local_metadata_t meta)
{
    // Description taken from NGSDN-TUTORIAL
    // Not used here. We assume all packets have valid checksum, if not, we let
    // the end hosts detect errors.
    apply { /* EMPTY */ }
}


control IngressPipeImpl (inout parsed_headers_t    hdr,
                         inout local_metadata_t    local_metadata,
                         inout standard_metadata_t standard_metadata) {

    // Drop action shared by many tables.
    action drop() {
        mark_to_drop(standard_metadata);
    }


    // *** L2 BRIDGING
    //
    // --- l2_exact_table (for unicast entries) --------------------------------

    action set_egress_port(port_num_t port_num, mac_addr_t dst_mac) {
        standard_metadata.egress_spec = port_num;
	// TO-DO: Update the destination mac address with the one received as parameter

	// TO-DO: Update the IPv4 TTL field to mark the packet traverses the switch
    }

    table ipv4_forward {
        key = {
            hdr.ipv4.dst_addr: exact;
        }
        actions = {
            set_egress_port;
            @defaultonly drop;
        }
    }

    action arp_reply(mac_addr_t request_mac) {
      //update operation code from request to reply
      hdr.arp.op_code = ARP_REPLY;

      //reply's dst_mac is the request's src mac
      hdr.arp.dst_mac = hdr.arp.src_mac;

      //reply's dst_ip is the request's src ip
      hdr.arp.src_mac = request_mac;

      //reply's src ip is the request's dst ip
      hdr.arp.src_ip = hdr.arp.dst_ip;

      //update ethernet header
      hdr.ethernet.dst_addr = hdr.ethernet.src_addr;
      hdr.ethernet.src_addr = request_mac;

      //send it back to the same port
      standard_metadata.egress_spec = standard_metadata.ingress_port;

    }


    table arp_exact {
      key = {
        hdr.arp.dst_ip: exact;
      }
      actions = {
        arp_reply;
        drop;
      }
      size = 1024;
      default_action = drop;
    }


   action nat_destination(ipv4_addr_t new_src_address, ipv4_addr_t new_dst_address, port_num_t dst_port, mac_addr_t dst_mac) {

	// TO-DO: The nat_destination action updates the ip address, the destination mac address
	// and sets the destination mac address and the outgoing port
   }



    table nat {
	key = {
		// TO-DO: The triggers of the NAT action are the destination MAC and IP addresses
		// The type of match is exact
	}
	actions = {
		nat_destination;
		drop;
	}
	size = 1024;
    }
		


    apply {

        if (hdr.ethernet.isValid() && hdr.ethernet.ether_type == ETHERTYPE_IPV4 && hdr.ipv4.isValid()){
		if (hdr.ipv4.protocol == IPV4_ICMP) {
			// TO-DO: Check the NAT table to update addresses, and do the IPv4 forwarding
		}
        } else if (hdr.ethernet.ether_type == ETHERTYPE_ARP) {
             arp_exact.apply();
        } 
    }
}


control EgressPipeImpl (inout parsed_headers_t hdr,
                        inout local_metadata_t local_metadata,
                        inout standard_metadata_t standard_metadata) {
    apply {


    }
}


control ComputeChecksumImpl(inout parsed_headers_t hdr,
                            inout local_metadata_t local_metadata)
{
    apply {
        update_checksum(
            hdr.ipv4.isValid(),
            {
		// TO-DO: The checksum is calculated on the fields of the IPv4 header
		// and updates the corresponding field of the header 
            },
            hdr.ipv4.checksum,
            HashAlgorithm.csum16);
    }
}


control DeparserImpl(packet_out packet, in parsed_headers_t hdr) {
    apply {
	packet.emit(hdr.ethernet);
	packet.emit(hdr.arp);
	packet.emit(hdr.ipv4);
    }
}


V1Switch(
    ParserImpl(),
    VerifyChecksumImpl(),
    IngressPipeImpl(),
    EgressPipeImpl(),
    ComputeChecksumImpl(),
    DeparserImpl()
) main;
