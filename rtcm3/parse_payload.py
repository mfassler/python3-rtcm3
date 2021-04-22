#!/usr/bin/env python3
  
import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

import struct
import bitstruct

from _3rd_party.pymap3d.ecef2geodetic import ecef2geodetic


## TODO:  This code is un-tested, but AFAICT, the only difference between
## msg_type 1005 and 1006 is the last field for "antenna height"
def decode_type1005(payload):
    '''
    Parse message type 1005:
        stationary rtk reference station ARP (antenna reference point)
    '''
    # 12 bits message type == 1005
    # 12 bits station ID
    #  6 bits itrf
    #  4 bits nothing?
    # 38 bits ecef-X (signed)
    #  2 bits nothing?
    # 38 bits ecef-Y (signed)
    #  2 bits nothing?
    # 38 bits ecef-Z (signed)

    assert len(payload) == 19

    msg_type, staid, itrf, _nothing, rrX, _nothing2, rrY, _nothing3, rrZ, \
        = bitstruct.unpack('u12u12u6u4s38u2s38u2s38', payload)

    print("\n * RTK base station ARP and antenna height")
    print("    - ECEF, meters: %.04f %.04f %.04f" % (rrX * 0.0001, rrY * 0.0001, rrZ * 0.0001))
    lat, lon, alt = ecef2geodetic(rrX * 0.0001, rrY * 0.0001, rrZ * 0.0001)

    print("    - Lat, Lon:", lat, lon)
    print("    - elevation, meters: %.04f" % (alt))
    print()


def decode_type1006(payload):
    '''
    Parse message type 1006:
        stationary rtk reference station ARP (antenna reference point) + antenna height
    '''
    # 12 bits message type == 1006
    # 12 bits station ID
    #  6 bits itrf
    #  4 bits nothing?
    # 38 bits ecef-X (signed)
    #  2 bits nothing?
    # 38 bits ecef-Y (signed)
    #  2 bits nothing?
    # 38 bits ecef-Z (signed)
    # 16 bits anth (antenna height?)

    assert len(payload) == 21

    msg_type, staid, itrf, _nothing, rrX, _nothing2, rrY, _nothing3, rrZ, \
        anth = bitstruct.unpack('u12u12u6u4s38u2s38u2s38u16', payload)

    print("\n * RTK base station ARP and antenna height")
    print("    - ECEF, meters: %.04f %.04f %.04f" % (rrX * 0.0001, rrY * 0.0001, rrZ * 0.0001))
    lat, lon, alt = ecef2geodetic(rrX * 0.0001, rrY * 0.0001, rrZ * 0.0001)

    print("    - Lat, Lon:", lat, lon)
    print("    - elevation, meters: %.04f" % (alt))
    print("    - antenna height:", anth)
    print()



def decode_msm_head(payload, _sys):    #, sync, iod, h, hsize):
    if _sys != 'GPS':
        print('unknown system')
        return
    # 12 bits message type
    # 12 bits station ID
    # 30 bits Time of Week (in milli-seconds)
    #  1 bit sync
    #  3 bits iod
    #  7 bits time_s
    #  2 bits clk_str
    #  2 bits clk_ext
    #  1 bit smooth
    #  3 bits tint_s
    # 64 bits Satellite mask
    msg_type, staid, tow_ms, sync, iod, time_s, clk_str, clk_ext, smooth, tint_s, \
        satmask = bitstruct.unpack('u12u12u30u1u3u7u2u2u1u3u64', payload)

    print('station id:', staid)
    print('sync:', sync)
    print('iod:', iod)
    print('time_s:', time_s)
    print('clk_str:', clk_str)
    print('clk_ext:', clk_ext)
    print('smooth:', smooth)
    print('tint_s:', tint_s)
    print('tow:', tow_ms * 0.001)

    print('satmask:', satmask)
    total_sats = 0
    for i in range(64):
        if ((satmask >> i) & 1) == 1:
            total_sats += 1
    print("Total sats:", total_sats)


def decode_msm5(pkt, _sys):
    decode_msm_head(pkt, _sys)


def decode_msm7(pkt, _sys):
    # msm7/GPS packet is approx 20 bytes + 15 bytes per satellite
    decode_msm_head(pkt, _sys)


def parse_payload(pkt):
    r3_type,  = bitstruct.unpack('u12', pkt)
    print("rtcm3 type: %d (%d bytes)" % (r3_type, len(pkt)))

    pktTypes = {
        1005: None,  # stationary rtk reference station arp
        1006: None,  # stationary rtk reference station arp + antenna height
        1033: None,  # receiver and antenna descriptors

        # "phaserangerate" means to correct for Doppler shift

        # the u-blox documentation seems to imply that "high-precision" is
        # mm-level accuracy, instead of cm-level accuracy

        # Docomo's NTRIP service seems to provide only msm5 messages.

        # u-blox documentation says to include 4072 messaes, which are
        # proprietary to u-blox

        # msm4:  full pseudorange and phaserange plus cnr
        # msm5:  full pseudorange, phaserange, phaserangerate and cnr
        # msm6:  full pseudorange and phaserange plus cnr (high-res)
        # msm7:  full pseudorange, phaserange, phaserangerate and cnr (h-res)

        1074: None,  # msm4, GPS
        1075: None,  # msm5, GPS
        1076: None,  # msm6, GPS
        1077: None,  # msm7, GPS

        1084: None,  # msm4, GLONASS
        1085: None,  # msm5, GLONASS
        1086: None,  # msm6, GLONASS
        1087: None,  # msm7, GLONASS

        1094: None,  # msm4, Galileo
        1095: None,  # msm5, Galileo
        1096: None,  # msm6, Galileo
        1097: None,  # msm7, Galileo

        1114: None,  # msm4, QZSS
        1115: None,  # msm5, QZSS
        1116: None,  # msm6, QZSS
        1117: None,  # msm7, QZSS

        1124: None,  # msm4, cmp -> BeiDou
        1125: None,  # msm5, cmp -> BeiDou
        1126: None,  # msm6, cmp -> BeiDou
        1127: None,  # msm7, cmp -> BeiDou

        1230: None,  # glonass L1, L2 code-phase bias

        # 4072.0 ublox proprietary message:  Reference station PVT
        # 4072.1 ublox proprietary message:  Additional reference station information
    }
    if r3_type not in pktTypes:
        print('  **** Unknown packet type:', r3_type)

    if r3_type == 1005:
        decode_type1005(pkt)

    elif r3_type == 1006:
        decode_type1006(pkt)

    elif r3_type == 1075:
        decode_msm5(pkt, 'GPS')

    elif r3_type == 1077:
        decode_msm7(pkt, 'GPS')
    return r3_type



