#!/usr/bin/env python3
  
import sys
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

import time
import base64
import struct
import select
import socket
import rtcm3


try:
    from NTRIP_PROVIDERS import ntrip_providors
except:
    from NTRIP_PROVIDERS_default import ntrip_providors


server_info = ntrip_providors['docomo']



def connect_and_auth(host_info):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 0))

    s.connect((host_info['host'], host_info['port']))
    s.send(b'GET /%s HTTP/1.0\r\n' % host_info['mount_point'].encode())
    s.send(b'User-Agent: NTRIP RTKLIB/2.4.3\r\n')

    basic_auth = base64.b64encode(host_info['username'].encode() + b':' + host_info['password'].encode())
    s.send(b'Authorization: Basic %s\r\n' % (basic_auth))
    s.send(b'\r\n')

    return s


# RX UDP packets from Moab-GPS receiver:
NMEA_RX_PORT = 27113
gps_sock_nmea = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
gps_sock_nmea.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
gps_sock_nmea.bind(("0.0.0.0", NMEA_RX_PORT))


# Connect to NTRIP server:
s = connect_and_auth(server_info)

time.sleep(0.2)
try:
    pkt2 = s.recv(10, socket.MSG_DONTWAIT)
except:
    pass
else:
    print(pkt2.decode())


packets = []
pTypes = []


while True:
    inputs, outputs, errors = select.select([gps_sock_nmea, s], [], [])
    for oneInput in inputs:
        if oneInput == s:
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
                    #gps_sock_nmea.sendto(pkt, ('192.168.8.201', 27113))
                    gps_sock_nmea.sendto(pkt, ('192.168.0.69', 27113))

        elif oneInput == gps_sock_nmea:
            pkt, addr = gps_sock_nmea.recvfrom(256)
            if b'GGA' in pkt:
                print(pkt)
                s.send(pkt)





