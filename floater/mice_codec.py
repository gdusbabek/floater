
Z = None

def encode_dst_addr(dst_ssid, lat, lon, msg_code):
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
    result = ''
    for n in range(7):  # TODO: not currently handling byte 6 (digi path lookup code). should be int(0..15)

        # characters 0..5
        lat_digit = lat.mice_digit(n)
        msg_bit = Z if n > 2 else _get_msg_code_bit(msg_code, n)
        ns = Z if n != 3 else lat.direction
        lon_offset = Z if n != 4 else 100 if lon.idegrees > 99 else 0
        we = Z if n != 5 else lon.direction

        if n == 6:
            # NOTE: the lookup table for the ssid is on p16.
            result += str(chr(dst_ssid))
        elif _is_south(ns) and _is_zero(lon_offset) and _is_east(we) and _is_zero(msg_bit):
            if lat_digit == ' ':
                result += 'L'
            else:
                result += lat_digit
        elif _is_oneS(msg_bit) and _is_north(ns) and _is_hundred(lon_offset) and _is_west(we):
            if lat_digit == ' ':
                result += 'Z'
            else:
                result += chr(ord(lat_digit) + 32)
        elif _is_oneC(msg_bit):
            if lat_digit == ' ':
                result += 'K'
            else:
                result += chr(ord(lat_digit) + 17)
        else:
            raise RuntimeError(f"didn't count on this: {n},({lat_digit},{msg_bit},{ns},{lon_offset},{we})")

    return result.encode('utf-8')

def clip(i, minimum, maximum):
    if i < minimum:
        return minimum
    elif i > maximum:
        return maximum
    else:
        return i

def decode_d28(ch, use_offset):
    """ decode longitude dgegrees. """
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

def encode_d28(v):
    """
    encodes the longitude degrees value. 0-179 degrees.
    returns a tuple if (char, used_lon_offset). used_lon_offset is a bit that means the
    decoded value will need to have 100 added to it. or something. I dunno.
    """
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

def decode_m28(ch):
    """ decode the longitude minutes. range is 0..60. """
    i = ord(ch)
    if i >= 88 and i <= 97:
        return i - 88
    elif i >= 38 and i <= 87:
        return i - 28
    else:
        return None

def encode_m28(v):
    """ encode the longitude minutes """
    if v >= 0 and v <= 9:
        return chr(88 + v)
    elif v >= 10 and v <= 59:
        return chr(v + 28)
    else:
        return None

def decode_h28(ch):
    """
    decode longitude hundredths of minutes (0 to 99 hundredths)
    """
    i = ord(ch)
    i -= 28
    return None if i < 0 or i > 99 else i

def encode_h28(v):
    """
    encode longitude hundredths of minutes to a char
    """
    if v < 0 or v > 99:
        return None
    else:
        return chr(v + 28)

def decode_sp28(ch):
    """
    decode the speed into 10s of knots. e.g. 10, 20, 110, 120, etc.
    """
    # l=108, DEL=127, x1c=28, /=47 ;; 0=48  k=107
    i = ord(ch)
    if i >= 108 and i <= 127:
        return 10 * (i - 108)
    elif i >= 28 and i <= 47:
        return 10 * (i - 28)
    elif i >= 48 and i <= 107:
        return 10 * (i - 48) + 200
    else:
        return None

def encode_sp28(speed_knots):
    """
    encode the speed. The result represents speed in units of 10 knots, e.g. 10, 20, 12, 130, etc.
    """
    spd = clip(speed_knots, 0, 799)
    factor = spd // 10
    if factor <= 19:
        return chr(108 + factor)
    else:  # factor >= 20
        return chr(48 + factor - 20)

def decode_dc28(ch):
    """
    returns a tuple of speed in ones of knots (0-9) and course in hundreds of degrees (100, 200, etc.)
    """
    speed = (ord(ch) - 28) // 10
    course = (((ord(ch) - 28) % 10) % 4) * 100
    return (speed, course)

def encode_dc28(speed, course):
    """
    encodes speed and course. Speed is modulo'd to 0..9 and course is bucketed to hundreds of degrees (100, 200, etc.)
    """
    # speed bucket is naturally 0..9
    # course (hundreds of degrees) buckets four ways: 0..3
    speed_bucket = speed % 10
    course_bucket = clip(course, 0, 360) // 100

    # there are 10 logical groupings in the table. each one is four characters long and can be indexed by the speed bucket.
    GROUPINGS = [ord(' '), ord('*'), ord('4'), ord('>'), ord('H'), ord('R'), ord('\\'), ord('f'), ord('p'), ord('z')]
    # could have also used this:
    # GROUPINGS = [ord('\x1c'), ord('&'), ord('0'), ord(':'), ord('D'), ord('N'), ord('X'), ord('b'), ord('l'), ord('v')]
    ch = chr(GROUPINGS[speed_bucket] + course_bucket)
    return ch


#
# Destination field helpers
#

def _is_south(ns):
    return True if ns == Z else ns == 'S'

def _is_north(ns):
    return True if ns == Z else ns == 'N'

def _is_zero(thing):
    if thing == Z:
        return True
    if thing == 0:
        return True
    if thing == '0':
        return True
    return False

def _is_hundred(thing):
    return True if thing == Z else thing == 100

def _is_east(we):
    return True if we == Z else we == 'E'

def _is_west(we):
    return True if we == Z else we == 'W'

def _is_oneS(msg_bit):
    return True if msg_bit == Z else msg_bit == '1s'

def _is_oneC(msg_bit):
    return True if msg_bit == Z else msg_bit == '1c'

#
# Message Code helpers
#

def _is_custom_msg_code(code):
    return code[0].startswith('C')

def _get_msg_code_bit(code, i):
    hilo = code[2][i]
    if hilo == '1':
        hilo += 'c' if _is_custom_msg_code(code) else 's'
    return hilo
