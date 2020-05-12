import floater.aprs as aprs

# 2934.94157N,09817.02034W

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

def test_decode_lon_digit():
    assert aprs.decode_lon_deg_ch('(', True) == 112

    # a few from 0..9
    assert aprs.decode_lon_deg_ch('&', True) != 10
    assert aprs.decode_lon_deg_ch('v', True) == 0
    assert aprs.decode_lon_deg_ch('~', True) == 8
    assert aprs.decode_lon_deg_ch(chr(127), True) == 9

    # a few from 10..99
    assert aprs.decode_lon_deg_ch('&', False) == 10
    assert aprs.decode_lon_deg_ch('v', False) == 90
    assert aprs.decode_lon_deg_ch('~', False) == 98
    assert aprs.decode_lon_deg_ch(chr(127), False) == 99

    # 100..109
    assert aprs.decode_lon_deg_ch('k', True) != 99
    assert aprs.decode_lon_deg_ch('l', True) == 100
    assert aprs.decode_lon_deg_ch('u', True) == 109
    assert aprs.decode_lon_deg_ch('v', True) != 110

    # 110..179
    assert aprs.decode_lon_deg_ch('%', True) != 109
    assert aprs.decode_lon_deg_ch('&', True) == 110
    assert aprs.decode_lon_deg_ch('k', True) == 179
    assert aprs.decode_lon_deg_ch('l', True) != 180

    # out of range. response is not specified.
    assert aprs.decode_lon_deg_ch('%', True) == None
    assert aprs.decode_lon_deg_ch('%', False) == None
    assert aprs.decode_lon_deg_ch(chr(128), True) == None
    assert aprs.decode_lon_deg_ch(chr(128), False) == None
