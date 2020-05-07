#!/usr/bin/env python3
  
import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

#import struct
import socket

import rtcm3


# This test is for use with AT-Drive Moab
UDP_PORT_MOAB_RTCM3 = 27117

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
udp_sock.bind(("0.0.0.0", UDP_PORT_MOAB_RTCM3))



packets = []
pTypes = []

while True:
    pkt, addr = udp_sock.recvfrom(1500)

    print()
    print('------------ new packet:')

    pkt = rtcm3.check_packet(pkt)

    if pkt is not None:
        print('rx packet: %d bytes' % (len(pkt)))
        payload = pkt[3:-3]
        pType = rtcm3.parse_payload(payload)
        pTypes.append(pType)

        packets.append(pkt)


