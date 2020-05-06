import serial
import time
import string
import pynmea2
import traceback
import logging

DEFAULT_UART_PORT = "/dev/ttyAMA0"

def collect(device=DEFAULT_UART_PORT, duration_secs=10):
    start = time.time()
    cur_time = start
    uart = None
    err_count = 0
    while cur_time - start < duration_secs and err_count < 5:

        # ensure serial connection.
        if not uart:
            uart = serial.Serial(port=device, baudrate=9600, timeout=0.5)
            if not uart:
                raise RuntimeError("Could not open serial connection to GPS")

        next_obj = None
        try:
            next_obj = _next_gps_object(uart)
        except:
            logging.debug("problem in next_gps_object()");
            traceback.print_exc()
        cur_time = time.time()
        if next_obj:
            yield next_obj

    if uart:
        uart.close()
    logging.debug("Leaving gps.collect()")


def _next_gps_object(uart, timeout=2):
    start_time = time.time()
    cur_time = start_time
    while True:
        gps_data = None
        try:
            bline = uart.readline()
            gps_data = _interpret_gps_line(bline)
        except pynmea2.ParseError:
            logging.debug("parse error. will try again.")
            continue
        except:
            traceback.print_exc
            time.sleep(0.5)
        cur_time = time.time()
        if gps_data:
            return gps_data
        if cur_time - start_time > timeout:
            break
    return None

def _interpret_gps_line(bline):
    if len(bline.strip()) < 7:
        return None
    msg_type = bline[0:6].decode('utf-8')

    # types with no data.
    if msg_type in ["$GPTXT", "$GPGSA", "$GPGSV"]:
        return None

    msg = pynmea2.parse(bline.decode('utf-8'))
    if isinstance(msg, pynmea2.RMC) or isinstance(msg, pynmea2.VTG) or isinstance(msg, pynmea2.GGA) or isinstance(msg, pynmea2.GLL):
        return msg
    else:
        logging.info(f"Unknown message: {msg_type} {repr(msg)}")
        return None

#
# TODO: Should be able to get rid of everything below here.
#       But gotta refactor `test_gps` mode first to use new methods.
#
def stream_from_file(file_path):
    with open(file_path) as fp:
        line = fp.readline()
        while line:
            yield line
            line = fp.readline()

def stream_from_device(device=DEFAULT_UART_PORT):
    uart = serial.Serial(
        port=device,
        baudrate=9600,
        timeout=0.5
    )
    while True:
        try:
            yield uart.readline()
        except:
            break
    uart.close()

def debug_line(line):
    try:
        if len(line.strip()) == 0:
            return
        msg_type = line[0:6].decode('utf-8')
        if msg_type in ["$GPTXT", "$GPGSA", "$GPGSV"]:
            return
        msg = pynmea2.parse(line.decode('utf-8'))
        if isinstance(msg, pynmea2.RMC):
            print(f"{msg.lat}{msg.lat_dir}, {msg.lon}{msg.lon_dir}, knots:{msg.spd_over_grnd}")
        elif isinstance(msg, pynmea2.VTG):
            print(f"kph:{msg.spd_over_grnd_kmph}, knots:{msg.spd_over_grnd_kts}")
        elif isinstance(msg, pynmea2.GGA):
            print(f"{msg.lat}{msg.lat_dir}, {msg.lon}{msg.lon_dir}, alt:{msg.altitude}{msg.altitude_units}, sats:{msg.num_sats}")
        elif isinstance(msg, pynmea2.GLL):
            print(f"{msg.lat}{msg.lat_dir}, {msg.lon}{msg.lon_dir}")
        else:
            print(f"UNKNOWN: {msg_type} {repr(msg)}")
    except pynmea2.nmea.ParseError:
        print('ouch')
        return
    except:
        print('double ouch')
        traceback.print_exc()

def debug_stream(open_func):
    for line in open_func():
        debug_line(line)