import os
from datetime import datetime

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
    """ input will probably be ddmm.hhhhhN, convert it into ddmm.hhM """
    return _encode_arbitrary_location(lat, 4)

def encode_longitude(lon):
    """ input will probably be dddmm.hhhhhW, convert it to dddmm.hhW """
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

def make_direwolf_string(bln, dst, via_digis, dt):
    return f"{bln.call}>{dst},{','.join(via_digis)}:{make_info_string(bln, dt)}"
