from datetime import datetime
import floater.aprs as aprs

# 2934.94157N,09817.02034W

def test_encode_call():
    assert aprs.encode_call('AAAAAA-11') == b'\x82\x82\x82\x82\x82\x82b'
    assert aprs.encode_call('BBBB-66') == b'\x84\x84\x84\x84@@l'
    assert aprs.encode_call('cccc') == b'\x86\x86\x86\x86@@`'
    assert aprs.encode_call('APRS') == b'\x82\xa0\xa4\xa6@@`'

def test_decode_call():
    assert aprs.decode_call(b'\x82\x82\x82\x82\x82\x82b') == 'AAAAAA-1'
    assert aprs.decode_call(b'\x84\x84\x84\x84@@l') == 'BBBB-6'
    assert aprs.decode_call(b'\x86\x86\x86\x86@@`') == 'CCCC-0'
    assert aprs.decode_call(b'\x82\xa0\xa4\xa6@@`') == 'APRS-0'

def test_encode_digis():
    assert aprs.encode_digis(['WIDE1-1', 'RELAY']) == b'\xae\x92\x88\x8ab@b\xa4\x8a\x98\x82\xb2@`'

def test_decode_digis():
    assert aprs.decode_digis(b'\xae\x92\x88\x8ab@b\xa4\x8a\x98\x82\xb2@`') == ['WIDE1-1', 'RELAY-0']

def test_encode_base91():
    assert len(aprs.BASE_91_DIGITS) == 91
    assert aprs.encode_base91(12345678) == '1Cmi'

def test_decode_base91():
    assert aprs.decode_base91('1Cmi') == 12345678

def test_get_times():
    dt = datetime.strptime("05/13/20 14:21:59", "%m/%d/%y %H:%M:%S")
    assert aprs.getHMS(dt) == '142159h'
    assert aprs.getDHM(dt) == '131421z'

def test_encode_latitude():
    assert aprs.encode_latitude('4903.50N') == '4903.50N'
    assert aprs.encode_latitude('4903.50n') == '4903.50N'
    assert aprs.encode_latitude('49.50N') == '4900.50N'
    assert aprs.encode_latitude('4903.5012N') == '4903.50N'

def test_encode_longitude():
    assert aprs.encode_longitude('07201.75W') == '07201.75W'
    assert aprs.encode_longitude('07201.75w') == '07201.75W'
    assert aprs.encode_longitude('07201.7521W') == '07201.75W'
    assert aprs.encode_longitude('072.75W') == '07200.75W'

def test_encode_position():
    assert aprs.encode_position('4903.50123N', '07201.75241W') == '4903.50N/07201.75WO'

def test_encode_altitude():
    assert aprs.encode_altitude(123) == '/A=000123'
    assert aprs.encode_altitude('123') == '/A=000123'
    assert aprs.encode_altitude(105000) == '/A=105000'