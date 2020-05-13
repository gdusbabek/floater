
#  the AX.25 frame
# 1 byte      : flag = b'\x7e'
# 7 bytes     : dest address, right padded, has a format
# 7 bytes     : source address, right padded, as a format
# 0-56 bytes  : digipeater addresses
# 1 byte      : control field = b'\x03'
# 1 byte      : protocol id = b'\xf0'
# 1-256 bytes : information field, format varies, but usually contains a header
# 2 bytes     : FCS checksum
# 1 byte      : flag, same as first.


FLAG = b'\x7e'
CTRL = b'\x03'
PCOL = b'\xf0'

""" 2934.94157N,09817.02034W """
class LatLon(object):
    def __init__(self, s):
        self.s = s

    def mice_digit(self, n):
        maybe_plus_one = 0 if self.is_lat else 1
        if n < 4:
            return self.s[n + maybe_plus_one]
        else:
            return self.s[n + 1 + maybe_plus_one]

    @property
    def is_lat(self):
        return self.direction in ['N', 'S']

    @property
    def direction(self):
        return self.s[-1]

    @property
    def is_north(self):
        return self.is_lat and self.direction == 'N'

    @property
    def sdegrees(self):
        end = 2 if self.is_lat else 3
        return self.s[0:end]

    @property
    def idegrees(self):
        return int(self.sdegrees.lstrip('0'))

    @property
    def sminutes(self):
        start = 2 if self.is_lat else 3
        return self.s[start:-1]

    @property
    def fminutes(self):
        return float(self.sminutes.strip('0'))

    def __repr__(self):
        return self.s

class MicE(object):
    def __init__(self, dst_ssid, src_addr, msg_code, lat, lon, course, speed):
        self.dst_ssid = dst_ssid
        self.src_addr = src_addr
        self.msg_code = msg_code
        self.lat = lat
        self.lon = lon

        self.course = ''
        self.speed = ''
        self.display_symbol = ''
        # todo: telemetry.


