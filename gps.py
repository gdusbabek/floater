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
    while cur_time - start < duration_secs:
        if not uart:
            uart = serial.Serial(port=device, baudrate=9600, timeout=0.5)
        try:
            yield next_gps_object(uart)
            cur_time = time.time()
        except UnicodeDecodeError:
            logging.debug("Problem device data (not unexpected")
            cur_time = time.time()
            continue
        except:
            traceback.print_exc()
            uart.close()
            break
    if uart:
        uart.close()
    logging.debug("Leaving gps.collect()")


def next_gps_object(uart, timeout=2):
    start_time = time.time()
    cur_time = start_time
    while True:
        bline = uart.readline()
        gps_data = interpret(bline)
        if gps_data:
            return gps_data
        if cur_time - start_time > timeout:
            break
    return None

def interpret(bline):
    if len(bline.strip()) < 7:
        return None
    msg_type = bline[0:6].decode('utf-8')

    # types with no data.
    if msg_type in ["$GPTXT", "$GPGSA", "$GPGSV"]:
        return None

    try:
        msg = pynmea2.parse(bline.decode('utf-8'))
        if isinstance(msg, pynmea2.RMC) or isinstance(msg, pynmea2.VTG) or isinstance(msg, pynmea2.GGA) or isinstance(msg, pynmea2.GLL):
            return msg
        else:
            logging.info(f"Unknow message: {msg_type} {repr(msg)}")
            return None
    except:
        traceback.print_exc()
        return None

# TODO: Should be able to get rid of everything below here.

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