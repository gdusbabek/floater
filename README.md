# Floater

This is still very much a WIP.
Some of the code works.

## Dependencies

* Imagemagick
* Direwolf

## Punchlist

- [x] mux control logic
- [x] turn on radio, activate ptt
- [x] stream gps data
- [x] get serious about some tests and project structure.
- [x] convert gps data into state
- [x] figure out correct APRS destination and digis.
- [ ] generate APRS telemetry messages.
- [x] generate APRS wav
- [x] collect gps to object
- [x] collect temperatures to object (wire in 18b20)
- [x] send APRS wav
- [x] physically connect sound to radio.
- [x] capture image
- [x] image to wav
- [x] create sstv reception station.
- [x] send image as sstv
- [ ] improve message quality on sstv picture.
- [ ] preflight check for devices.
- [ ] video capture is not happening according to schedule.
- [ ] battery meter solution (for desperate measures)
- [ ] logic around emergency shutdown, power-up etc.
- [ ] automation around initial set up.
- [ ] configuration file.

## Run things on the tracker

Get things there:
```bash
scp -r floater/*.py *.txt *.md pi@192.168.86.32:/home/pi/fc/
```

Run it:
```bash
# maybe update the venv:
source /home/pi/tracker_env/bin/activate
pip install -r /home/pi/fc/requirements.txt
PYTHONPATH=/home/pi/fc/ /home/pi/tracker_env/bin/python /home/pi/fc/flight_controller.py --init
```

Other options: `--test-gps`, `--test-vhf`

Copy images and stuff back:
```bash
scp pi@192.168.86.32:/home/pi/Pictures/photos/capture_0139.jpg ~/Desktop/test_photos/
```

## Using Direwolf is cheating

I know. I have a [branch](https://github.com/gdusbabek/floater/tree/native_afsk) that has a native
APRS + AX.25 + AFSK implementation, but the wav files that get generated are worthless. :(