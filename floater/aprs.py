
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

class SSID(object):
    ID_0 = ('0', 'Use VIA Path')
    ID_1 = ('1', 'WIDE1-1')
    ID_2 = ('2', 'WIDE2-2')
    ID_3 = ('3', 'WIDE3-3')
    ID_4 = ('4', 'WIDE4-4')
    ID_5 = ('5', 'WIDE5-5')
    ID_6 = ('6', 'WIDE6-6')
    ID_7 = ('7', 'WIDE7-7')
    ID_8 = ('8', 'North path')
    ID_9 = ('9', 'South path')
    ID_10 = ('10', 'East path')
    ID_11 = ('11', 'West path')
    ID_12 = ('12', 'North path + WIDE')
    ID_13 = ('13', 'South path + WIDE')
    ID_14 = ('14', 'East path + WIDE')
    ID_15 = ('15', 'West path + WIDE')

    @staticmethod
    def normalize(key_or_tuple):
        key = None
        if isinstance(key_or_tuple, tuple):
            key = key_or_tuple[0]
        elif isinstance(key_or_tuple, int):
            key = str(key_or_tuple)
        else:
            raise RuntimeError(f"Unexpected reference: {key_or_tuple}")
        return {
            '0': SSID.ID_0,
            '1': SSID.ID_1,
            '2': SSID.ID_2,
            '3': SSID.ID_3,
            '4': SSID.ID_4,
            '5': SSID.ID_5,
            '6': SSID.ID_6,
            '7': SSID.ID_7,
            '8': SSID.ID_8,
            '9': SSID.ID_9,
            '10': SSID.ID_10,
            '11': SSID.ID_11,
            '12': SSID.ID_12,
            '13': SSID.ID_13,
            '14': SSID.ID_14,
            '15': SSID.ID_15
        }[key]

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

    def encode_dst_addr_char(self, n):
        """
        mic-e destination address field (p43)
        byte 0 : lat digit 1 + msg bit A
        byte 1 : lat digit 2 + msg bit b
        byte 2 : lat digit 3 + msg bit c
        byte 3 : lat digit 4 + north/south latitude indicator bit
        byte 4 : lat digit 5 + longitude offset indicator bit (0=0º, 1=100º)
        byte 5 : lat digit 6 + west/east longitude indicator bit
        byte 6 : aprs digi path code (note: could stuff other thigns here. we only 4 bits.)
        """
        if n < 0 or n > 6:
            raise RuntimeError(f"Invalid destination address index: {n}")
        elif n == 6:
            # NOTE: the lookup table for the ssid is on p16.
            return self.dst_ssid.encode('utf-8')

        # characters 0..5
        lat_digit = self.lat.mice_digit(n)
        msg_bit = Z if n > 2 else MsgCodes.get_msg_bit(self.msg_code, n)
        ns = Z if n != 3 else self.lat.direction
        lon_offset = Z if n != 4 else 100 if self.lon.idegrees > 99 else 0
        we = Z if n != 5 else self.lon.direction

        if DstField.south(ns) and DstField.zero(lon_offset) and DstField.east(we) and DstField.zero(msg_bit):
            if lat_digit == ' ':
                return b'L'
            else:
                return lat_digit.encode('utf-8')
        elif DstField.oneS(msg_bit) and DstField.north(ns) and DstField.hundred(lon_offset) and DstField.west(we):
            if lat_digit == ' ':
                return b'Z'
            else:
                return chr(ord(lat_digit) + 32).encode('utf-8')
        elif DstField.oneC(msg_bit):
            if lat_digit == ' ':
                return b'K'
            else:
                return chr(ord(lat_digit) + 17).encode('utf-8')
        else:
            raise RuntimeError(f"didn't count on this: {n},({lat_digit},{msg_bit},{ns},{lon_offset},{we})")

    def encode_info_char(self, n):
        """
        mic-e information field (p46)
        byte 0 : data type id
        bytes 2,3,4 : longitude
        bytes 4,5,6 : speed and course
        byte 7 : symbol code
        byte 8 : symbol table id
        more bytes : either mic-e telemetry or mic-e status text.
        """
        pass

def decode_lon_deg_ch(ch, use_offset):
    """
    To decode the longitude degrees value:
    1. subtract 28 from the d+28 value to obtain d.
    2. if the longitude offset is +100 degrees, add 100 to d.
    3. subtract 80 if 180 <= d <= 189
    (i.e. the longitude is in the range 100–109 degrees).
    4. or, subtract 190 if 190 <= d <= 199.
    (i.e. the longitude is in the range 0–9 degrees).
    """
    d = ord(ch)
    # quick range check. any character outside of this range is invalid.
    if d < 38 or d > 127:
        return None

    # account for the +28.
    d -= 28
    if use_offset:
        d += 100
    if d >= 180 and d <= 189:
        d -= 80
    elif d >= 190 and d <= 199:
        d -= 190
    return d

def encode_lon_deg_value(v):
    if v >= 0 and v <= 9:
        return (chr(118 + v), True)
    elif v >= 10 and v <= 99:
        return (chr(v + 28), False)
    elif v >= 100 and v <= 109:
        return (chr(v + 8), True)
    elif v >= 110 and v <= 179:
        return (chr(v - 72), True)
    else:
        return None


def decode_lon_min_ch(ch):
    i = ord(ch)
    if i >= 88 and i <= 97:
        return i - 88
    elif i >= 38 and i <= 87:
        return i - 28
    else:
        return None

def encode_lon_min_value(v):
    if v >= 0 and v <= 9:
        return chr(88 + v)
    elif v >= 10 and v <= 59:
        return chr(v + 28)
    else:
        return None

def decode_lon_hun_ch(ch):
    i = ord(ch)
    i -= 28
    return None if i < 0 or i > 99 else i

def encode_lon_hun_value(v):
    if v < 0 or v > 99:
        return None
    else:
        return chr(v + 28)