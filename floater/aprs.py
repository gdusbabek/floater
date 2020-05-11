
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

Z = None

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

class MsgCodes(object):
    MO = ("M0", "Off Duty", "111")
    M1 = ("M1", "En Route", "110")
    M2 = ("M2", "In Service", "101")
    M3 = ("M3", "Returning", "100")
    M4 = ("M4", "Committed", "011")
    M5 = ("M5", "Special", "010")
    M6 = ("M6", "Priority", "001")
    C0 = ("C0", "Custom-0", "111")
    C1 = ("C1", "Custom-1", "110")
    C2 = ("C2", "Custom-2", "101")
    C3 = ("C3", "Custom-3", "100")
    C4 = ("C4", "Custom-4", "011")
    C5 = ("C5", "Custom-5", "010")
    C6 = ("C6", "Custom-6", "001")
    EM = (None, "Emergency", "000")

    @staticmethod
    def is_custom(code):
        return code[0].startswith('C')

    @staticmethod
    def get_msg_bit(code, i):
        hilo = code[2][i]
        if hilo == '1':
            hilo += 'c' if MsgCodes.is_custom(code) else 's'
        return hilo

class DstField(object):

    @staticmethod
    def south(ns):
        return True if ns == Z else ns == 'S'

    @staticmethod
    def north(ns):
        return True if ns == Z else ns == 'N'

    @staticmethod
    def zero(thing):
        if thing == Z:
            return True
        if thing == 0:
            return True
        if thing == '0':
            return True
        return False

    @staticmethod
    def hundred(thing):
        return True if thing == Z else thing == 100

    @staticmethod
    def east(we):
        return True if we == Z else we == 'E'

    @staticmethod
    def west(we):
        return True if we == Z else we == 'W'

    @staticmethod
    def oneS(msg_bit):
        return True if msg_bit == Z else msg_bit == '1s'

    @staticmethod
    def oneC(msg_bit):
        return True if msg_bit == Z else msg_bit == '1c'

class MicE(object):
    def __init__(self, msg_code, lat, lon, course, speed):
        self.msg_code = msg_code
        self.lat = lat
        self.lon = lon

        self.course = ''
        self.speed = ''
        self.display_symbol = ''
        # todo: telemetry.

    def dest_tuple(self, n):
        lat_digit = self.lat.mice_digit(n - 1)
        msg_bit = Z if n > 3 else MsgCodes.get_msg_bit(self.msg_code, n - 1)
        ns = Z if n != 4 else self.lat.direction
        lon_offset = Z if n != 5 else 100 if self.lon.idegrees > 99 else 0
        we = Z if n != 6 else self.lon.direction

        if DstField.south(ns) and DstField.zero(lon_offset) and DstField.east(we) and DstField.zero(msg_bit):
            if lat_digit == ' ':
                return 'L'
            else:
                return lat_digit
        elif DstField.oneS(msg_bit) and DstField.north(ns) and DstField.hundred(lon_offset) and DstField.west(we):
            if lat_digit == ' ':
                return 'Z'
            else:
                return chr(ord(lat_digit) + 32)
        elif DstField.oneC(msg_bit):
            if lat_digit == ' ':
                return 'K'
            else:
                return chr(ord(lat_digit) + 17)
        else:
            raise RuntimeError(f"didn't count on this: {n},({lat_digit},{msg_bit},{ns},{lon_offset},{we})")
