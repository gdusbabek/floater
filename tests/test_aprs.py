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
    mic = aprs.MicE(aprs.MsgCodes.M3, aprs.LatLon('3325.6400N'), aprs.LatLon('01010.1010W'), None, None)
    assert mic.dest_tuple(1) == 'S'
    assert mic.dest_tuple(2) == '3'
    assert mic.dest_tuple(3) == '2'
    assert mic.dest_tuple(4) == 'U'
    assert mic.dest_tuple(5) == '6'
    assert mic.dest_tuple(6) == 'T'