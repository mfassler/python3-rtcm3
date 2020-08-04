#!/usr/bin/env python3
  
import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

import struct
import socket

import rtcm3


NTRIP_HOST = 'rtk2go.com'
NTRIP_MOUNT_POINT = 'YC-FUKUROI'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 0))
s.connect((NTRIP_HOST, 2101))

s.send(b'GET /%s HTTP/1.0' % NTRIP_MOUNT_POINT.encode())
s.send(b'')


packets = []
pTypes = []

while True:
    aa = s.recv(1)
    if len(aa) == 0:
        continue

    c = ord(aa)

    if c == 0xd3:

        plen_raw_bytes = s.recv(2)
        plen_raw, =  struct.unpack('!H', plen_raw_bytes)
        plen = 0x03ff & plen_raw

        #print("length:", plen)
        head = b'\xd3' + plen_raw_bytes
        payload = s.recv(plen)
        cksum_bytes = s.recv(3)

        pkt = head + payload + cksum_bytes

        print()
        print('------------ new packet:')

        pkt = rtcm3.check_packet(pkt)

        if pkt is not None:
            print('rx packet: %d bytes' % (len(pkt)))
            payload = pkt[3:-3]
            pType = rtcm3.parse_payload(payload)
            pTypes.append(pType)

            packets.append(pkt)


