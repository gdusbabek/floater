import os
from datetime import datetime
import itertools
import pytest
import floater.aprs as aprs

# 2934.94157N,09817.02034W

@pytest.fixture
def simple_balloon():
    b = aprs.State()
    b.call = 'N0CALL'
    b.lat = '4903.50123N'
    b.lon = '07201.7521W'
    b.ground_speed_knots = 156
    b.raw_altitude = str(int(round(75344 / 3.28084))) + 'M'
    b.course = 65
    return b

@pytest.fixture
def simple_zulu():
    dt = datetime.strptime("05/13/20 14:21:59", "%m/%d/%y %H:%M:%S")
    return dt


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
    assert aprs.make_info_string(simple_balloon, simple_zulu) == '@142159h4903.50N/07201.75WO065/156/A=075344'

def test_make_direwolf_string(simple_balloon, simple_zulu):
    # echo -n "N0CALL>APN25,WIDE1-1,WIDE2-1:@142159h4903.50N/07201.75WO065/156/A=075345" | ./gen_packets -a 25 -o /tmp/test_file_3.wav -
    actual = aprs.make_direwolf_string(simple_balloon, 'APN25', ["WIDE1-1", "WIDE2-1"], simple_zulu)
    expected = 'N0CALL>APN25,WIDE1-1,WIDE2-1:@142159h4903.50N/07201.75WO065/156/A=075344 sat=None in= out= sstv=0'
    assert actual == expected

def test_make_wav(simple_balloon, simple_zulu):
    if not os.environ.get('DIREWOLF_HOME'):
        return
    wav_path = '/tmp/test_file_5.wav'
    aprs_string = aprs.make_direwolf_string(simple_balloon, 'APN25', ['WIDE1-1', 'WIDE2-1'], simple_zulu)
    aprs.make_wav(aprs_string, wav_path)
    assert os.path.exists(wav_path)