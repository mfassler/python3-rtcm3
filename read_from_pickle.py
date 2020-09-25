#!/usr/bin/env python3
  
import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

import pickle

from _3rd_party.pymap3d.ecef2geodetic import ecef2geodetic

import rtcm3


f = open(sys.argv[1], 'rb')
packets = pickle.load(f)
f.close()


for pkt in packets:
    pkt = rtcm3.check_packet(pkt)
    payload = pkt[3:-3]
    pType = rtcm3.parse_payload(payload)



