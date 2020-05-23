
import sys
import argparse
import time
from datetime import datetime
import traceback
import logging
logging.basicConfig(level=logging.DEBUG)

import gpio
import gps
import dra818
import aprs
import cam
import therm

def check_devices():
    pass

def update_gps(state):
    gpio.enable_gps()
    logging.debug("Taking GPS reading")
    start_time = time.time()
    for msg in gps.collect():
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
            state.raw_altitude = msg.altitude
        if hasattr(msg, 'altitude_units'):
            state.raw_altitude = str(state.raw_altitude) + msg.altitude_units

        if time.time() - start_time > 10000:
            break
    logging.debug("Done with reading.")

def update_temps(state):
    logging.debug("Getting temparatures")
    state.temp_in = therm.get_internal_temp()
    state.temp_out = therm.get_external_temp()

def capture_photo(state):
    photo_path = cam.capture_photo()
    logging.info(f"Captured photo to: {photo_path}.")
    state.last_photo_time = time.time()
    state.last_photo_path = photo_path

def capture_video(state):
    video_path = cam.capture_video()
    logging.info(f"Captured video to: {video_path}.")
    state.last_video_time = time.time()
    state.last_video_path = video_path

def send_aprs(state, aprs_dst='APN25', digis=['WIDE1-1']):
    gpio.enable_vhf()
    now = datetime.utcnow()
    try:
        aprs_string = aprs.make_direwolf_string(state, aprs_dst, digis, now)
    except:
        traceback.print_exc()
        logging.error('Not sending APRS')
        return

    wav_path = '/tmp/aprs.wav'
    aprs.make_wav(aprs_string, wav_path)

    if not dra818.program(frequency=146.500):
        logging.error("Problem programming")
        sys.exit(1)
    logging.info(f'Sending APRS: {{{aprs_string}}}')
    # dra818.ptt(True)
    try:
        time.sleep(0.25)
        dra818.play_file(wav_path)
        time.sleep(0.25)
    except:
        traceback.print_exc()
    dra818.ptt(False)


def send_sstv(state):
    logging.info(f'SSTV send not implemented, but would send {state.last_photo_path}')


def restart_pi():
    pass


def main(args):

    if args.call is None:
        logging.critical("You need to set the `call` parameter. ")
        sys.exit(-1)

    logging.info("Welcome to the main event!")
    try:
        gpio.init_pins()
        logging.info("Pi GPIO initialized. Checking devices.")
    except:
        # not a good sign.
        logging.critical("Could not initialize GPIO. Restarting device")
        restart_pi()

    check_devices()
    state = aprs.State()

    state.call = args.call

    while True:
        loop_start = time.time()
        try:
            low_disk = False  # TODO: implement this check.
            state.will_send_sstv = loop_start - state.last_sstv_time > 300000
            update_gps(state)
            update_temps(state)
            logging.info('gps and temperatures recorded')
            if state.is_valid():
                send_aprs(state)
            else:
                logging.warning("Invalid state. Will not APRS")
                logging.warning(f'{repr(state)}')
            logging.info('beacon sent')
            capture_photo(state)
            if state.will_send_sstv:
                logging.info('starting sstv send')
                send_sstv(state)
                logging.info('sstv send completed')
                state.last_sstv_time = time.time()
            if not low_disk and loop_start - state.last_video_time > 300000:
                logging.info('capturing video')
                capture_video(state)
                state.last_video_time = time.time()
        except:
            # ugh.
            traceback.print_exc()

        logging.debug(repr(state))

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
    parser.add_argument("--test-photo", action="store_true", default=False, help="Capture a test photo")
    parser.add_argument("--test-video", action="store_true", default=False, help="Capture a test video")
    parser.add_argument("--test-therm", action="store_true", default=False, help="Display temperatures")

    parser.add_argument("--call", type=str, help="Call sign + SSID of balloon. e.g. N0CALL-1")

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
        line_count = 50
        for msg in gps.collect(duration_secs=250):
            line_count -= 1
            logging.debug(repr(msg))
            if line_count <= 0:
                break
    elif args.test_vhf:
        logging.info("Testing VHF. Short broadcast on 146.500MHz")
        gpio.init_pins()
        gpio.enable_vhf()
        if not dra818.program(frequency=146.500):
            logging.error("Problem programming")
            sys.exit(1)
        logging.info("Programed OK")
        dra818.ptt(True)
        time.sleep(5)
        dra818.ptt(False)
    elif args.test_photo:
        photo_path = cam.capture_photo()
        logging.info(f"Captured test photo: {photo_path}.")
    elif args.test_video:
        video_path = cam.capture_video()
        logging.info(f"Captured test video: {video_path}.")
    elif args.test_therm:
        logging.info(f"Internal temp: {therm.get_internal_temp()}")
        logging.info(f"External temp: {therm.get_external_temp()}")
    else:
        main(args)
        sys.exit(0)
