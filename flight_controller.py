
import sys
import argparse
import serial
import time
import logging
logging.basicConfig(level=logging.DEBUG)

import gpio
import gps
import dra818

class State(object):
    def __init__(self):
        self.long = 0.0
        self.lat = 0.0
        self.bearing = 0.0
        self.speed = 0.0
        self.radio_freq = 0.0


def check_devices():
    pass

def update_gps(state):
    gpio.enable_gps()
    start_time = time.time()
    for msg in gps.collect():
        logging.info(f"MSG: {repr(msg)}")
        if time.time() - start_time > 10000:
            break
    logging.debug("Leaving update_gps")

def update_temps(state):
    pass


def send_aprs(state):
    pass


def send_sstv(state):
    pass


def restart_pi():
    pass


def main(args):

    try:
        gpio.init_pins()
        logging.info("Pi GPIO initialized. Checking devices.")
    except:
        # not a good sign.
        logging.critical("Could not initialize GPIO. Restarting device")
        restart_pi()

    check_devices()
    last_sstv = 0
    state = State()

    while True:
        loop_start = time.time()
        try:
            update_gps(state)
            update_temps(state)
            send_aprs(state)
            if (time.time() - last_sstv) > 300000:
                last_sstv = time.time()
                send_sstv(state)
        except:
            pass

        # maybe take a nap.
        loop_end = time.time()
        sleep_time = max(0, 60 - loop_end + loop_start)
        if sleep_time > 0:
            logging.info(f"Sleeping {sleep_time}s")
            time.sleep(sleep_time)
        else:
            logging.info("Not sleeping")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true", default=False, help="Initializes UART multiplexers to a safe state")
    parser.add_argument("--test-gps", action="store_true", default=False, help="Tests the GPS")
    parser.add_argument("--test-vhf", action="store_true", default=False, help="Test VHF radio with a short broadcast to 146.500")

    parser.add_argument("--aprs-frequency", type=float, default=144.390, help="APRS Transmit Frequency (MHz)")
    parser.add_argument("--sstv-frequency", type=float, default=146.500, help="Frequency used to send SSTV images")
    parser.add_argument("--uart-device", type=str, default='/dev/ttyAMA0', help="Serial port connected to module.")
    parser.add_argument("--test", action="store_true", default=False, help="Cycle through all devices testing them.")
    args = parser.parse_args()

    if args.init:
        logging.info("Initializing")
        gpio.init_pins()
    elif args.test_gps:
        logging.info("Enabling GPS. Check out /dev/ttyAMA0")
        gpio.init_pins()
        gpio.enable_gps()
        line_count = 100
        for line in gps.stream_from_device():
            line_count -= 1
            gps.debug_line(line)
            if line_count <= 0:
                break
    elif args.test_vhf:
        logging.info("Testing VHF. Short broadcast on 146.500MHz")
        gpio.init_pins()
        gpio.enable_vhf()
        ok = dra818.program(frequency=146.500)
        if not ok:
            logging.error("Problem programming")
            sys.exit(1)
        dra818.ptt(True)
        time.sleep(5)
        dra818.ptt(False)
    else:
        main(args)
        sys.exit(0)