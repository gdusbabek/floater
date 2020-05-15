import os
from datetime import datetime
import itertools
import pytest
import floater.aprs as aprs

# 2934.94157N,09817.02034W

@pytest.fixture
def simple_balloon():
    b = aprs.BalloonInfo()
    b.call = 'N0CALL'
    b.lat = '4903.50123N'
    b.lon = '07201.7521W'
    b.speed_knots = 156
    b.altitude_in_feet = 75345
    b.course = 65
    return b

@pytest.fixture
def simple_zulu():
    dt = datetime.strptime("05/13/20 14:21:59", "%m/%d/%y %H:%M:%S")
    return dt

# def test_generator_detection():
#     def gen_func():
#         for x in range(5):
#             yield x

#     ## test some baseline assumptions about pass by reference.
#     def mutate_list(l):
#         l[0] = 100
#     def really_mutate_list(l):
#         l.pop(0)
#     my_list = [x for x in range(5)]
#     assert my_list == [0,1,2,3,4]
#     mutate_list(my_list)
#     assert my_list == [100,1,2,3,4]
#     really_mutate_list(my_list)
#     assert my_list == [1,2,3,4]

#     assert len(gen_func()) == 1

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
    assert aprs.encode_digis(['WIDE1-1', 'RELAY']) == b'\xae\x92\x88\x8ab@b\xa4\x8a\x98\x82\xb2@a'

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

def test_encode_course_and_speed():
    assert aprs.encode_course_and_speed(34, 21) == '034/021'
    assert aprs.encode_course_and_speed(0, 21) == '360/021'
    assert aprs.encode_course_and_speed(1, 121) == '001/121'

def test_make_info_string(simple_balloon, simple_zulu):
    assert aprs.make_info_string(simple_balloon, simple_zulu) == '@142159h4903.50N/07201.75WO065/156/A=075345'

def test_fcs():
    data = b'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    fcs_digest = aprs.make_fcs(data)
    assert fcs_digest == b'[\x07'

def test_make_aprs_packet(simple_balloon, simple_zulu):
    packet = aprs.packet(simple_balloon, "APRS", ["WIDE1-1", "WIDE2-1"], simple_zulu)
    expected = b"~\x82\xa0\xa4\xa6@@`\x9c`\x86\x82\x98\x98`\xae\x92\x88\x8ab@b\xae\x92\x88\x8ad@c\x03\xe8 \x18\x9a\x19\x18\x9a\x9c\xb4\x1a\x1c\x98\x19\x97\x1a\x98'\x17\x98\x1b\x99\x18\x18\x97\x1b\x9a\xab\xa7\x98\x1b\x1a\x97\x98\x9a\x9b\x17\xa0\x9e\x98\x1b\x9a\x99\x9a\x1a\x90\xe9\x80~"
    assert packet == expected

def test_make_wav(simple_balloon, simple_zulu):
    # clean up any debris
    wav_path = '/tmp/test_file.wav'
    if os.path.exists(wav_path):
        os.remove(wav_path)
    assert not os.path.exists(wav_path)

    packet = aprs.packet(simple_balloon, 'APRS', ['WIDE1-1', 'WIDE2-1'], simple_zulu)
    aprs.packet_to_wav(packet, wav_path)
    assert os.path.exists(wav_path)
