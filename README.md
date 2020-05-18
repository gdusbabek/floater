# Floater

This is still very much a WIP.
Some of the code works.

## Punchlist

- [x] mux control logic
- [x] turn on radio, activate ptt
- [x] stream gps data
- [x] get serious about some tests and project structure.
- [x] convert gps data into state
- [x] generate APRS wav
- [x] collect gps to object
- [ ] collect temperatures to object (waiting on 4.7k resistors)
- [ ] send APRS wav
- [ ] capture image
- [ ] send image as sstv
- [ ] capture temperature
- [ ] battery meter solution (for desperate measures)
- [ ] logic around emergency shutdown, power-up etc.
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
