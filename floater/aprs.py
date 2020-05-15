import os
import struct
from datetime import datetime
from bitstring import BitArray, Bits
import audiogen
from floater import afsk

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

class BalloonInfo(object):
    def __init__(self):
        self.call = ''
        self.lat = ''
        self.lon = ''
        self.speed_kmh = 0
        self.speed_knots = 0
        self.altitude_in_feet = 0
        self.temp_in = ''
        self.temp_out = ''
        self.course = 0

def zulu_now():
    return datetime.utcnow()

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
    # encoded_digi_array = [encode_call(d) for d in digis]
    # return b''.join(encoded_digi_array)

    encoded_digi_array = bytearray(b''.join([encode_call(d) for d in digis]))

    # saw this getting done somewhere...
    # I don't think it should really matter. Here's why:
    # during decode everything gets shifted one bit to the right, so this falls off.
    # the argument for it was to know when the digis end, but the control field does
    # a good job of that, so whatevs.
    # I'm doing this for sake of compatibility.
    encoded_digi_array[-1] |= 0x01

    return encoded_digi_array

def decode_digis(digis_bytes):
    if len(digis_bytes) % 7 != 0:
        raise RuntimeError(f"Invalid array length; cannot decode digis ({len(digis_bytes)}")

    digis_bytes = bytearray(digis_bytes)  # make it mutable so the next line works.

    # unscrew the last byte.
    digis_bytes[-1] &= 0xfe

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

# Data extensions

def encode_course_and_speed(course, speed_in_knots):
    course %= 360
    if course == 0:
        course = 360
    return f"{str(course).zfill(3)}/{str(speed_in_knots).zfill(3)}"

## Put it all together

def make_info_string(balloon, dt):
    # generally speaking, the aprs info section is like this:
    # 1 - data type id. we are going to want '/' which is pos w/timestamp (will include other nice things)
    # n - aprs data (position w/ timestamp). maybe figure out how do do compressed lat/lon/course/speed/range/alt.
    # 7 - aprs data extension (course and speed)
    # m - aprs comment (altitude)
    # everyone complains about base91, but it's only used for compressed lat/lon (ch9) and altitude in mic-e.
    # everyone should be complaining about the bit-shifting in addresses. that crap is madness.
    symbol_table_id = '/'
    symbol_code = 'O'
    data = f"@{getHMS(dt)}"
    data += f"{encode_latitude(balloon.lat)}{symbol_table_id}{encode_longitude(balloon.lon)}{symbol_code}"
    data += f"{encode_course_and_speed(balloon.course, balloon.speed_knots)}"
    data += f"{encode_altitude(balloon.altitude_in_feet)}"
    # we still have room for 36-9=27 bytes in the comment.
    return data

def make_fcs(byte_data):
    fcs = 0xffff
    for byte in byte_data:
        for i in range(7, -1, -1):
            bit = (byte >> i) & 0x01 == 1
            check = fcs & 0x1 == 1
            fcs >>= 1
            if check != bit:
                fcs ^= 0x8408

    # make the digest
    return struct.pack('<H', ~fcs % 2**16)

def packet(balloon_info, destination, via_digis, zulu_dt):
    # these are bytes
    dst = encode_call(destination)
    src = encode_call(balloon_info.call)
    digis = encode_digis(via_digis)

    # info is a string, so be sure to convert it to bytes.
    info = make_info_string(balloon_info, zulu_dt).encode('ascii')

    data = dst + src + digis + CTRL + PCOL + info
    fcs = make_fcs(data)

    # i hate myself.
    def stuff(byte_data):
        count = 0
        for bit in afsk._as_bits(byte_data):
            if bit:
                count += 1
            else:
                count = 0
            yield bit
            if count == 5:
                yield False
                count = 0

    return FLAG + BitArray(stuff(data + fcs)).tobytes() + FLAG

def packet_to_wav(packet, file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(file_path):
        raise RuntimeError(f"Could not remove {file_path}")

    audio = afsk.encode(packet)
    with open(file_path, 'wb') as f:
        audiogen.sampler.write_wav(f, audio)
