#!/usr/bin/env python3
  
import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

import struct



def getbitu(buff, pos, length):
    bits = 0
    for i in range(pos, pos+length):
        bits <<= 1
        bits += buff[i//8] >> (7-i%8) & 0x01

    return bits


#f = open('/tmp/tow.txt', 'w')

GPS_LEAP_SECONDS = 0 # 18
def decode_msm_head(pkt, _sys):    #, sync, iod, h, hsize):
    staid = getbitu(pkt, 12, 12)
    print('station id:', staid)
    if _sys == 'GPS':
        tow = getbitu(pkt, 24, 30) * 0.001 - GPS_LEAP_SECONDS
        print('tow:', tow)
        #f.write("tow: %s \n" % (tow))
        #f.flush()
    else:
        print('unknown system')
        return
    sync    = getbitu(pkt, 54, 1)  # multiple message indicator
    iod     = getbitu(pkt, 55, 3)  # Issue of Data station
    time_s  = getbitu(pkt, 58, 7)
    clk_str = getbitu(pkt, 65, 2) # clock steering
    clk_ext = getbitu(pkt, 67, 2) # external clock
    smooth  = getbitu(pkt, 69, 1)  # bool
    tint_s  = getbitu(pkt, 70, 3)  # smoothing interval

    satmask = getbitu(pkt, 73, 64)
    print('satmask:', satmask)
    total_sats = 0
    for i in range(64):
        if ((satmask >> i) & 1) == 1:
            total_sats += 1
    print("Total sats:", total_sats)


def decode_msm7(pkt, _sys):
    # msm7/GPS packet is approx 20 bytes + 15 bytes per satellite
    decode_msm_head(pkt, _sys)


def parse_payload(pkt):
    r3_type = (pkt[0] << 4) | ((pkt[1] & 0xf0) >> 4)
    #r3_type = getbitu(pkt, 0, 12)
    print("rtcm3 type:", r3_type, len(pkt))
    pktTypes = {
        1005: None,  # stationary rtk reference station arp
        1074: None,  # msm4, GPS
        1077: None,  # msm7, GPS
        1084: None,  # msm4, GLONASS
        1087: None,  # msm7, GLONASS
        1094: None,  # msm4, Galileo
        1097: None,  # msm7, Galileo
        1124: None,  # msm4, cmp -> BeiDou
        1127: None,  # msm7, cmp -> BeiDou
        1230: None,  # glonass L1, L2 code-phase bias
        # 4072.0 ?
        # 4072.1 ?
    }
    if r3_type not in pktTypes:
        print('  **** Unknown packet type:', r3_type)
    print(r3_type, len(pkt))
    if r3_type == 1077:
        decode_msm7(pkt, 'GPS')
    return r3_type




