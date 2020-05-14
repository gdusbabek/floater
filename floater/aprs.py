from bitstring import BitArray
from datetime import datetime

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
BASE_91_DIGITS = [chr(i + 33) for i in range(91)]

class LatLon(object):
    def __init__(self, s):
        self.s = s

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

class BalloonInfo(object):
    def __init__(self):
        self.call = ''
        self.lat = ''
        self.lon = ''
        self.speed_kmh = ''
        self.altitude = ''
        self.temp_in = ''
        self.temp_out = ''
        self.course = ''

def encode_call(addr):
    # split into (addr, ssid)
    addr = addr.upper()
    if addr.find('-') > 0:
        addr, ssid = addr.split('-')
    else:
        ssid = '0'

    # adjust addr, ssid in case they are out of range.
    addr = addr[:6] if len(addr) > 6 else addr
    ssid = ssid[:1] if len(ssid) > 1 else ssid

    # convert to bytes and shift left one bit.
    call = f"{addr:6s}{ssid}".encode('ascii')
    call_bytes = BitArray(call)
    call_bytes.rol(1)
    return call_bytes.tobytes()

def decode_call(call_bytes):
    # read in and shift right one bit.
    cb = BitArray(call_bytes)
    cb.ror(1)
    call = cb.tobytes().decode('ascii')

    # separate call and ssid. ssid is at the end. there may be whitespace in between them.
    ssid = call[-1]
    call = call[:-1].strip()
    return f"{call}-{ssid}"

def encode_digis(digis):
    encoded_digi_array = [encode_call(d) for d in digis]
    return b''.join(encoded_digi_array)

def decode_digis(digis_bytes):
    if len(digis_bytes) % 7 != 0:
        raise RuntimeError(f"Invalid array length; cannot decode digis ({len(digis_bytes)}")
    digis = [digis_bytes[n*7:(n+1)*7] for n in range(len(digis_bytes) // 7)]  # noqa: E226
    digis = [decode_call(d) for d in digis]
    return digis

def encode_base91(num):
    if num < 0:
        raise ValueError(f"Input should be >= zero ({num})")
    elif num == 0:  # easy case.
        return BASE_91_DIGITS[0]
    digits = []
    while num:
        digits.append(BASE_91_DIGITS[int(num % 91)])
        num //= 91
    digits.reverse()
    return ''.join(digits)

## BYTES DEMARCATOR: everything below here does not return bytes. Maybe fix that?

def decode_base91(s):
    num = 0
    for i, ch in enumerate(s):
        num += BASE_91_DIGITS.index(ch) * (91 ** (len(s) - 1 - i))
    return num

# don't use this format in status reports.
def getHMS(dt):
    return dt.strftime('%H%M%S') + 'h'

def getDHM(dt):
    return dt.strftime('%d%H%M') + 'z'

# 2934.94157N,09817.02034W

def _encode_arbitrary_location(lonlat, w):
    dm, h = lonlat.split('.')
    d = h[-1].upper()  # direction
    h = h[:-1]  # git rid of direction
    while len(dm) < w:
        dm += '0'
    while len(h) > 2:
        h = h[:-1]
    return f"{dm}.{h}{d}"

def encode_latitude(lat):
    """
    input will probably be ddmm.hhhhhN
    convert it into ddmm.hhM
    """
    return _encode_arbitrary_location(lat, 4)

def encode_longitude(lon):
    """
    input will probably be dddmm.hhhhhW.
    convert it to dddmm.hhW
    """
    return _encode_arbitrary_location(lon, 5)

def encode_position(lat, lon, table='/', symbol='O'):
    return f"{encode_latitude(lat)}{table}{encode_longitude(lon)}{symbol}"

def encode_altitude(alt_in_feet):
    if isinstance(alt_in_feet, int):
        alt_in_feet = str(alt_in_feet)
    return f"/A={alt_in_feet.zfill(6)}"

def make_info_string(balloon):
    # generally speaking, the aprs info section is like this:
    # 1 - data type id. we are going to want '/' which is pos w/timestamp (will include other nice things)
    # n - aprs data
    # 7 - aprs data extension
    # m - aprs comment
    # everyone complains about base91, but it's only used for compressed lat/lon (ch9) and altitude in mic-e.
    # everyone should be complaining about the bit-shifting in addresses. that crap is madness.
    return ''


def make_aprs_packet(ballon_info, destination, via_digis):
    return b"{flag}{dst}{src}{digis}{ctrl}{pcol}".format(
        flag=FLAG,
        dst=encode_call(destination),
        src=encode_call(ballon_info.call),
        digis=encode_digis(via_digis),
        ctrl=CTRL,
        pcol=PCOL
    )


