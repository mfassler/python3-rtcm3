#!/usr/bin/env python3

import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

import struct

from rtcm3.parse_payload import parse_payload

def CRC24(msg):
    CRC24_INIT = 0xb704ce
    CRC24_POLY = 0x1864cfb
    CRC24_OUTMASK = 0xffffff

    crc = 0 #CRC24_INIT
    for c in msg:

        crc ^= (c << 16)

        for i in range(8):
            crc <<= 1
            if (crc & 0x1000000):
                crc ^= 0x01864cfb

    return crc & CRC24_OUTMASK


def check_packet(pkt):
    '''
    an RTCM3 packet is:
      1 byte:  0xd3  (magic start byte)
      2 bytes:  payload length  (big-endian, max size is 1023)
       ... payload ...
      3 bytes:  checksum
    '''
    assert pkt[0] == 0xd3
    plen, = struct.unpack('!H', pkt[1:3])
    if len(pkt) != (plen + 6):
        print("WARN: wrong packet size.  Packet is %d bytes, but header says %d" % (len(pkt), plen+6))
        pkt = pkt[:plen+6]

    check = CRC24(pkt[0: -3])
    cksum = (pkt[-3] << 16) | (pkt[-2] << 8) | pkt[-1]

    if check == cksum:
        return pkt
    else:
        print('bad CRC.  Expected: 0x%x, got: 0x%x' % (check, cksum))
        return None



