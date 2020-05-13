import floater.mice_codec as codec
import floater.aprs as aprs
from floater.constants import MsgCodes

DEL = chr(127)

def test_map_of_tuples():
    m = {
        ('a','b','c') : '0',
        ('a','b',1) : '1'
    }
    assert m[('a','b','c')] == '0'
    assert m[('a','b',1)] == '1'

def test_first_six_mice_encoding():
    dst_ssid = 0
    msg_code = MsgCodes.M3
    lat = aprs.LatLon('3325.6400N')
    lon = aprs.LatLon('01010.1010W')

    assert codec.encode_dst_addr(dst_ssid, lat, lon, msg_code) == b'S32U6T\x00'

def test_decode_d28_lon_deg():
    assert codec.decode_d28('(', True) == 112

    # a few from 0..9
    assert codec.decode_d28('&', True) != 10
    assert codec.decode_d28('v', True) == 0
    assert codec.decode_d28('~', True) == 8
    assert codec.decode_d28(DEL, True) == 9

    # a few from 10..99
    assert codec.decode_d28('&', False) == 10
    assert codec.decode_d28('v', False) == 90
    assert codec.decode_d28('~', False) == 98
    assert codec.decode_d28(DEL, False) == 99

    # 100..109
    assert codec.decode_d28('k', True) != 99
    assert codec.decode_d28('l', True) == 100
    assert codec.decode_d28('u', True) == 109
    assert codec.decode_d28('v', True) != 110

    # 110..179
    assert codec.decode_d28('%', True) != 109
    assert codec.decode_d28('&', True) == 110
    assert codec.decode_d28('k', True) == 179
    assert codec.decode_d28('l', True) != 180

    # out of range. response is not specified.
    assert codec.decode_d28('%', True) == None
    assert codec.decode_d28('%', False) == None
    assert codec.decode_d28(chr(128), True) == None
    assert codec.decode_d28(chr(128), False) == None

def test_encode_d28_lon_deg():
    assert codec.encode_d28(0) == ('v', True)
    assert codec.encode_d28(8) == ('~', True)
    assert codec.encode_d28(9) == (DEL, True)

    assert codec.encode_d28(10) == ('&', False)
    assert codec.encode_d28(90) == ('v', False)
    assert codec.encode_d28(98) == ('~', False)
    assert codec.encode_d28(99) == (DEL, False)

    assert codec.encode_d28(110) == ('&', True)
    assert codec.encode_d28(179) == ('k', True)

    assert codec.encode_d28(180) == None

def test_decode_m28_lon_min():
    assert codec.decode_m28('X') == 0
    assert codec.decode_m28('a') == 9
    assert codec.decode_m28('&') == 10
    assert codec.decode_m28('W') == 59

    assert codec.decode_m28('%') == None
    assert codec.decode_m28('b') == None

def test_encode_m28_lon_min():
    assert codec.encode_m28(0) == 'X'
    assert codec.encode_m28(9) == 'a'
    assert codec.encode_m28(10) == '&'
    assert codec.encode_m28(59) == 'W'

    assert codec.encode_m28(-1) == None
    assert codec.encode_m28(60) == None

def test_decode_h28_lon_hun():
    assert codec.decode_h28('&') == 10
    assert codec.decode_h28(DEL) == 99

    assert codec.decode_h28(chr(27)) == None
    assert codec.decode_h28(chr(128)) == None

def test_encode_h28_lon_hun():
    assert codec.encode_h28(10) == '&'
    assert codec.encode_h28(99) == DEL

    assert codec.encode_h28(-1) == None
    assert codec.encode_h28(100) == None

def test_decode_sp28_coarse_speed():
    assert codec.decode_sp28('l') == 0
    assert codec.decode_sp28(chr(28)) == 0
    assert codec.decode_sp28('s') == 70
    assert codec.decode_sp28('#') == 70

    assert codec.decode_sp28('7') == 270
    assert codec.decode_sp28('k') == 790

    assert codec.decode_sp28(chr(10)) == None

def test_encode_sp28_coarse_speed():
    assert codec.encode_sp28(-1) == 'l'
    assert codec.encode_sp28(0) == 'l'
    assert codec.encode_sp28(73) == 's'
    assert codec.encode_sp28(275) == '7'
    assert codec.encode_sp28(799) == 'k'
    assert codec.encode_sp28(7990) == 'k'

def test_decode_dc28_fine_speed_and_course():
    assert codec.decode_dc28(' ') == codec.decode_dc28('\x1c') == (0, 0)
    assert codec.decode_dc28('+') == codec.decode_dc28('\'') == (1, 100)
    assert codec.decode_dc28('6') == codec.decode_dc28('2') == (2, 200)
    assert codec.decode_dc28('A') == codec.decode_dc28('=') == (3, 300)
    assert codec.decode_dc28('H') == codec.decode_dc28('D') == (4, 0)
    assert codec.decode_dc28('S') == codec.decode_dc28('O') == (5, 100)
    assert codec.decode_dc28('^') == codec.decode_dc28('Z') == (6, 200)
    assert codec.decode_dc28('i') == codec.decode_dc28('e') == (7, 300)
    assert codec.decode_dc28('p') == codec.decode_dc28('l') == (8, 0)
    assert codec.decode_dc28('{') == codec.decode_dc28('w') == (9, 100)

def test_encode_dc28_fine_speed_and_course():
    assert codec.encode_dc28(10, 50) == ' '
    assert codec.encode_dc28(21, 121) == '+'
    assert codec.encode_dc28(32, 222) == '6'
    assert codec.encode_dc28(43, 359) == 'A'
    assert codec.encode_dc28(54, 70) == 'H'
    assert codec.encode_dc28(65, 160) == 'S'
    assert codec.encode_dc28(76, 297) == '^'
    assert codec.encode_dc28(87, 320) == 'i'
    assert codec.encode_dc28(98, 14) == 'p'
    assert codec.encode_dc28(109, 195) == '{'
