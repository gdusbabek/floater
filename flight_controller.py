
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
        self.lon = None
        self.lat = None
        self.ground_speed_knots = 0.0
        self.ground_speed_kph = 0.0
        self.timestamp = None
        self.datestamp = None
        self.sats = None
        self.altitude = None

        self.radio_freq = 0.0

    def __repr__(self):
        return f"alt:{self.altitude} {self.lat},{self.lon} spd:{self.ground_speed_kph}({self.ground_speed_knots}) sats:{self.sats}"


def check_devices():
    pass

def update_gps(state):
    gpio.enable_gps()
    logging.info("Taking GPS reading")
    start_time = time.time()
    for msg in gps.collect():
        # logging.debug(f"MSG: {repr(msg)}")
        if hasattr(msg, 'lat'):
            state.lat = msg.lat
        if hasattr(msg, 'lon'):
            state.lon = msg.lon
        if hasattr(msg, 'lat_dir'):
            state.lat += msg.lat_dir
        if hasattr(msg, 'lon_dir'):
            state.lon += msg.lon_dir
        if hasattr(msg, 'timestamp'):
            state.timestamp = msg.timestamp
        if hasattr(msg, 'datestamp'):
            state.datestamp = msg.datestamp
        if hasattr(msg, 'spd_over_grnd_kts'):
            state.ground_speed_knots = msg.spd_over_grnd_kts
        if hasattr(msg, 'spd_over_grnd_kmph'):
            state.ground_speed_kph = msg.spd_over_grnd_kmph
        if hasattr(msg, 'num_sats'):
            state.sats = msg.num_sats
        if hasattr(msg, 'altitude'):
            state.altitude = msg.altitude
        if hasattr(msg, 'altitude_units'):
            state.altitude = str(state.altitude) + msg.altitude_units

        if time.time() - start_time > 10000:
            break
    logging.debug("Done with reading.")

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
        for msg in gps.collect():
            line_count -= 1
            logging.debug(repr(msg))
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