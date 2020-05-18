import os
import subprocess
from datetime import datetime
import logging

DIREWOLF_HOME = os.environ.get('DIREWOLF_HOME')

class State(object):
    def __init__(self):
        self.call = ''
        self.lon = ''
        self.lat = ''
        self.ground_speed_knots = 0
        self.ground_speed_kph = 0
        self.timestamp = None
        self.datestamp = None
        self.sats = None
        self.raw_altitude = ''
        self.temp_in = ''
        self.temp_out = ''
        self.course = 0
        self.radio_freq = 0.0

        self.last_photo_time = 0
        self.last_video_time = 0
        self.last_sstv_time = 0
        self.will_send_sstv = False

    def __repr__(self):
        return f"alt:{self.raw_altitude} {self.lat},{self.lon} spd:{self.ground_speed_kph}({self.ground_speed_knots}) sats:{self.sats}"

    def is_valid(self):
        return len(self.lon.strip()) > 0 and \
            len(self.lat.strip()) > 0

def zulu_now():
    return datetime.utcnow()

# don't use this format in status reports.
def getHMS(dt):
    return dt.strftime('%H%M%S') + 'h'

def getDHM(dt):
    return dt.strftime('%d%H%M') + 'z'

# 2934.94157N,09817.02034W

def _encode_arbitrary_location(lonlat, w):
    try:
        dm, h = lonlat.split('.')
        d = h[-1].upper()  # direction
        h = h[:-1]  # git rid of direction
        while len(dm) < w:
            dm += '0'
        while len(h) > 2:
            h = h[:-1]
        return f"{dm}.{h}{d}"
    except ValueError:
        logging.error(f'Problem encoding this: {lonlat}   {w}')
        return '0'

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

def alt_to_feet(alt):
    if alt is None:
        return 0
    elif alt.lower().endswith('m'):
        return int(round(int(float(alt[:-1])) * 3.28084))
    else:
        return int(alt[:-1])

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
    data += f"{encode_course_and_speed(balloon.course, balloon.ground_speed_knots)}"
    data += f"{encode_altitude(alt_to_feet(balloon.raw_altitude))}"
    # we still have room for 36-9=27 bytes in the comment.
    return data

def make_direwolf_string(bln, dst, via_digis, dt):
    s = f"{bln.call}>{dst},{','.join(via_digis)}:{make_info_string(bln, dt)}"
    s += f" sat={bln.sats} in={bln.temp_in} out={bln.temp_out} sstv={1 if bln.will_send_sstv else 0}"
    return s

def make_wav(bln, dst, via_digis, dt, wav_path):
    if not DIREWOLF_HOME:
        raise RuntimeError('Cannot find direwolf. Check env (export DIREWOLF_HOME=...)')
    dw_str = make_direwolf_string(bln, dst, via_digis, dt)
    if os.path.exists(wav_path):
        os.remove(wav_path)
    if os.path.exists(wav_path):
        raise RuntimeError('Could not remove old wav file')
    # subprocess.check_output(f'echo -n {dw_str} | {DIREWOLF_HOME}/gen_packets -a 25 -o {wav_path} -', shell=True)
    echo = subprocess.Popen(['echo', '-n', dw_str], stdout=subprocess.PIPE)
    gen_packets = subprocess.Popen([f"{DIREWOLF_HOME}/gen_packets", '-a', '25', '-o', wav_path, '-'], stdin=echo.stdout)
    echo.stdout.close()
    gen_packets.communicate()
    if not os.path.exists(wav_path):
        raise RuntimeError('Could not generate wave file')
