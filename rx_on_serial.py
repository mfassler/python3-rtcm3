#!/usr/bin/env python3
  
import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

import struct
#import serial

import rtcm3

#ser = serial.Serial('/dev/ttyACM0', 115200)
#f = open('/dev/ttyUSB0', 'rb')
f = open(sys.argv[1], 'rb')


packets = []
pTypes = []

while True:
    aa = f.read(1)
    if len(aa) == 0:
        continue

    c = ord(aa)

    if c == 0xd3:
        #print(f.tell())

        plen_raw_bytes = f.read(2)
        plen_raw, =  struct.unpack('!H', plen_raw_bytes)
        plen = 0x03ff & plen_raw

        #print("length:", plen)
        head = b'\xd3' + plen_raw_bytes
        payload = f.read(plen)
        cksum_bytes = f.read(3)

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


