import os
import time
import logging

# can't do any harm, right?
os.system('modprobe w1-therm')

BASE_DIR         = '/sys/bus/w1/devices/'
EXT_THERM_DEVICE = '28-8a20160fa0ff'
INT_THERM_DEVICE = '28-8a201605ecff'


def _get_raw_lines(device_path):
    with open(device_path) as f:
        return f.readlines()

def _get_temp(device, fc, timeout):
    """
    Data looks something like this:
    pi@balloon02:~ $ cat /sys/bus/w1/devices/28-8a20160fa0ff/w1_slave
    b8 01 55 00 7f ff 0c 10 8c : crc=8c YES
    b8 01 55 00 7f ff 0c 10 8c t=27500

    So two lines. If the CRC checks ot, the temperature is thousanths of degrees celsius.
    This means that "27500" is 27.5C
    """
    start = time.time()
    device_file = os.path.join('/sys/bus/w1/devices/', device, 'w1_slave')
    while (time.time() - start < timeout):
        raw_lines = _get_raw_lines(device_file)
        if raw_lines[0].strip().endswith('YES'):
            eq_pos = raw_lines[1].find('t=')
            temp_str = raw_lines[1][eq_pos + 2:]
            temp_c = float(temp_str) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return round(temp_f, 1) if fc.lower() == 'f' else round(temp_c, 1)
        else:
            logging.debug(f"raw line 0: {raw_lines[0]}")
            time.sleep(0.2)
    logging.warn("Could not get temperature")
    return None

def get_internal_temp(fc='f', timeout=5):
    return _get_temp(INT_THERM_DEVICE, fc, timeout)

def get_external_temp(fc='f', timeout=5):
    return _get_temp(EXT_THERM_DEVICE, fc, timeout)
