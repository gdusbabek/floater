import floater.aprs as aprs

# 2934.94157N,09817.02034W

DEL = chr(127)

def test_normal_lat_parse():
    spec = "2934.94157N"
    l = aprs.LatLon(spec)
    assert l.is_lat
    assert l.sdegrees == '29'
    assert l.idegrees == 29
    assert l.sminutes == '34.94157'
    assert l.fminutes == 34.94157
    assert l.direction == 'N'
    assert repr(l) == spec

def test_lon_parse_less_than_100():
    spec = "09817.02034W"
    l = aprs.LatLon(spec)
    assert not l.is_lat
    assert l.sdegrees == '098'
    assert l.idegrees == 98
    assert l.sminutes == '17.02034'
    assert l.fminutes == 17.02034
    assert l.direction == 'W'
    assert repr(l) == spec

def test_long_parse_more_than_100():
    spec = "12117.02034W"
    l = aprs.LatLon(spec)
    assert not l.is_lat
    assert l.sdegrees == '121'
    assert l.idegrees == 121
    assert l.sminutes == '17.02034'
    assert l.fminutes == 17.02034
    assert l.direction == 'W'
    assert repr(l) == spec

def test_minute_trimming():
    spec = "2934.04100N"
    l = aprs.LatLon(spec)
    assert l.is_lat
    assert l.fminutes == 34.041
    assert l.sminutes == '34.04100'
    assert l.direction == 'N'

def test_lat_digits():
    spec = "1234.5678N"
    l = aprs.LatLon(spec)
    assert l.mice_digit(0) == '1'
    assert l.mice_digit(1) == '2'
    assert l.mice_digit(2) == '3'
    assert l.mice_digit(3) == '4'
    assert l.mice_digit(4) == '5'
    assert l.mice_digit(5) == '6'

def test_lon_digits():
    spec = "01234.5678W"
    l = aprs.LatLon(spec)
    assert l.mice_digit(0) == '1'
    assert l.mice_digit(1) == '2'
    assert l.mice_digit(2) == '3'
    assert l.mice_digit(3) == '4'
    assert l.mice_digit(4) == '5'
    assert l.mice_digit(5) == '6'

def test_map_of_tuples():
    m = {
        ('a','b','c') : '0',
        ('a','b',1) : '1'
    }
    assert m[('a','b','c')] == '0'
    assert m[('a','b',1)] == '1'

def test_first_six_mice_encoding():
    mic = aprs.MicE(0, "N0CALL", aprs.MsgCodes.M3, aprs.LatLon('3325.6400N'), aprs.LatLon('01010.1010W'), None, None)
    assert mic.encode_dst_addr_char(0) == b'S'
    assert mic.encode_dst_addr_char(1) == b'3'
    assert mic.encode_dst_addr_char(2) == b'2'
    assert mic.encode_dst_addr_char(3) == b'U'
    assert mic.encode_dst_addr_char(4) == b'6'
    assert mic.encode_dst_addr_char(5) == b'T'

def test_decode_lon_deg_ch():
    assert aprs.decode_d28('(', True) == 112

    # a few from 0..9
    assert aprs.decode_d28('&', True) != 10
    assert aprs.decode_d28('v', True) == 0
    assert aprs.decode_d28('~', True) == 8
    assert aprs.decode_d28(DEL, True) == 9

    # a few from 10..99
    assert aprs.decode_d28('&', False) == 10
    assert aprs.decode_d28('v', False) == 90
    assert aprs.decode_d28('~', False) == 98
    assert aprs.decode_d28(DEL, False) == 99

    # 100..109
    assert aprs.decode_d28('k', True) != 99
    assert aprs.decode_d28('l', True) == 100
    assert aprs.decode_d28('u', True) == 109
    assert aprs.decode_d28('v', True) != 110

    # 110..179
    assert aprs.decode_d28('%', True) != 109
    assert aprs.decode_d28('&', True) == 110
    assert aprs.decode_d28('k', True) == 179
    assert aprs.decode_d28('l', True) != 180

    # out of range. response is not specified.
    assert aprs.decode_d28('%', True) == None
    assert aprs.decode_d28('%', False) == None
    assert aprs.decode_d28(chr(128), True) == None
    assert aprs.decode_d28(chr(128), False) == None

def test_encode_lon_deg_digit():
    assert aprs.encode_d28(0) == ('v', True)
    assert aprs.encode_d28(8) == ('~', True)
    assert aprs.encode_d28(9) == (DEL, True)

    assert aprs.encode_d28(10) == ('&', False)
    assert aprs.encode_d28(90) == ('v', False)
    assert aprs.encode_d28(98) == ('~', False)
    assert aprs.encode_d28(99) == (DEL, False)

    assert aprs.encode_d28(110) == ('&', True)
    assert aprs.encode_d28(179) == ('k', True)

    assert aprs.encode_d28(180) == None

def test_decode_m28_lon_min():
    assert aprs.decode_m28('X') == 0
    assert aprs.decode_m28('a') == 9
    assert aprs.decode_m28('&') == 10
    assert aprs.decode_m28('W') == 59

    assert aprs.decode_m28('%') == None
    assert aprs.decode_m28('b') == None

def test_encode_m28_lon_min():
    assert aprs.encode_m28(0) == 'X'
    assert aprs.encode_m28(9) == 'a'
    assert aprs.encode_m28(10) == '&'
    assert aprs.encode_m28(59) == 'W'

    assert aprs.encode_m28(-1) == None
    assert aprs.encode_m28(60) == None

def test_decode_h28_lon_hun():
    assert aprs.decode_h28('&') == 10
    assert aprs.decode_h28(DEL) == 99

    assert aprs.decode_h28(chr(27)) == None
    assert aprs.decode_h28(chr(128)) == None

def test_encode_h28_lon_hun():
    assert aprs.encode_h28(10) == '&'
    assert aprs.encode_h28(99) == DEL

    assert aprs.encode_h28(-1) == None
    assert aprs.encode_h28(100) == None

def test_decode_sp28_coarse_speed():
    assert aprs.decode_sp28('l') == 0
    assert aprs.decode_sp28(chr(28)) == 0
    assert aprs.decode_sp28('s') == 70
    assert aprs.decode_sp28('#') == 70

    assert aprs.decode_sp28('7') == 270
    assert aprs.decode_sp28('k') == 790

    assert aprs.decode_sp28(chr(10)) == None

def test_encode_sp28_coarse_speed():
    assert aprs.encode_sp28(-1) == 'l'
    assert aprs.encode_sp28(0) == 'l'
    assert aprs.encode_sp28(73) == 's'
    assert aprs.encode_sp28(275) == '7'
    assert aprs.encode_sp28(799) == 'k'
    assert aprs.encode_sp28(7990) == 'k'

def test_decode_dc28_fine_speed_and_course():
    assert aprs.decode_dc28(' ') == aprs.decode_dc28('\x1c') == (0, 0)
    assert aprs.decode_dc28('+') == aprs.decode_dc28('\'') == (1, 100)
    assert aprs.decode_dc28('6') == aprs.decode_dc28('2') == (2, 200)
    assert aprs.decode_dc28('A') == aprs.decode_dc28('=') == (3, 300)
    assert aprs.decode_dc28('H') == aprs.decode_dc28('D') == (4, 0)
    assert aprs.decode_dc28('S') == aprs.decode_dc28('O') == (5, 100)
    assert aprs.decode_dc28('^') == aprs.decode_dc28('Z') == (6, 200)
    assert aprs.decode_dc28('i') == aprs.decode_dc28('e') == (7, 300)
    assert aprs.decode_dc28('p') == aprs.decode_dc28('l') == (8, 0)
    assert aprs.decode_dc28('{') == aprs.decode_dc28('w') == (9, 100)

def test_encode_dc28_fine_speed_and_course():
    assert aprs.encode_dc28(10, 50) == ' '
    assert aprs.encode_dc28(21, 121) == '+'
    assert aprs.encode_dc28(32, 222) == '6'
    assert aprs.encode_dc28(43, 359) == 'A'
    assert aprs.encode_dc28(54, 70) == 'H'
    assert aprs.encode_dc28(65, 160) == 'S'
    assert aprs.encode_dc28(76, 297) == '^'
    assert aprs.encode_dc28(87, 320) == 'i'
    assert aprs.encode_dc28(98, 14) == 'p'
    assert aprs.encode_dc28(109, 195) == '{'
