import logging

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    logging.error("Could not load RPi GPIO library. Running in dev mode.")
    import fake_gpio as GPIO
except RuntimeError:
    logging.critical("Could not load RPi GPIO library.")

"""
 +-----+-----+---------+------+---+-Pi ZeroW-+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 |     |     |    3.3v |      |   |  1 || 2  |   |      | 5v      |     |     |
 |   2 |   8 |   SDA.1 |   IN | 1 |  3 || 4  |   |      | 5v      |     |     |
 |   3 |   9 |   SCL.1 |   IN | 1 |  5 || 6  |   |      | 0v      |     |     |
 |   4 |   7 | GPIO. 7 |   IN | 1 |  7 || 8  | 1 | ALT0 | TxD     | 15  | 14  |
 |     |     |      0v |      |   |  9 || 10 | 1 | ALT0 | RxD     | 16  | 15  |
 |  17 |   0 | GPIO. 0 |   IN | 0 | 11 || 12 | 0 | IN   | GPIO. 1 | 1   | 18  |
 |  27 |   2 | GPIO. 2 |   IN | 0 | 13 || 14 |   |      | 0v      |     |     |
 |  22 |   3 | GPIO. 3 |   IN | 0 | 15 || 16 | 0 | IN   | GPIO. 4 | 4   | 23  |
 |     |     |    3.3v |      |   | 17 || 18 | 0 | IN   | GPIO. 5 | 5   | 24  |
 |  10 |  12 |    MOSI |   IN | 0 | 19 || 20 |   |      | 0v      |     |     |
 |   9 |  13 |    MISO |   IN | 0 | 21 || 22 | 0 | IN   | GPIO. 6 | 6   | 25  |
 |  11 |  14 |    SCLK |   IN | 0 | 23 || 24 | 1 | IN   | CE0     | 10  | 8   |
 |     |     |      0v |      |   | 25 || 26 | 1 | IN   | CE1     | 11  | 7   |
 |   0 |  30 |   SDA.0 |   IN | 1 | 27 || 28 | 1 | IN   | SCL.0   | 31  | 1   |
 |   5 |  21 | GPIO.21 |   IN | 1 | 29 || 30 |   |      | 0v      |     |     |
 |   6 |  22 | GPIO.22 |   IN | 1 | 31 || 32 | 0 | IN   | GPIO.26 | 26  | 12  |
 |  13 |  23 | GPIO.23 |   IN | 0 | 33 || 34 |   |      | 0v      |     |     |
 |  19 |  24 | GPIO.24 |   IN | 0 | 35 || 36 | 0 | IN   | GPIO.27 | 27  | 16  |
 |  26 |  25 | GPIO.25 |   IN | 0 | 37 || 38 | 0 | IN   | GPIO.28 | 28  | 20  |
 |     |     |      0v |      |   | 39 || 40 | 0 | IN   | GPIO.29 | 29  | 21  |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+-Pi ZeroW-+---+------+---------+-----+-----+
"""

HIGH                = GPIO.HIGH
LOW                 = GPIO.LOW

# We are using the Broadcom (BCM) layout.

TEMP_DATA           = 4  # PHYS 7
TEMP_VCC            = 25 # PHYS 22

TX_MUX_E            = 3  # PHYS 5
TX_MUX_S0           = 17 # PHYS 11
TX_MUX_S1           = 27 # PHYS 13
TX_MUX_S2           = 22 # PHYS 15
TX_MUX_Z            = 14 # PHYS 8

RX_MUX_E            = 5  # PHYS 29
RX_MUX_S0           = 10 # PHYS 19
RX_MUX_S1           = 9  # PHYS 21
RX_MUX_S2           = 11 # PHYS 23
RX_MUX_Z            = 15 # PHYS 10

VHF_PTT             = 6  # PHYS 31
VHF_HL              = 13 # PHYS 33
VHF_PD              = 19 # PHYS 35

# order: S0, S1, S2
Y0_PINS             = (GPIO.LOW, GPIO.LOW, GPIO.LOW)
Y1_PINS             = (GPIO.HIGH, GPIO.LOW, GPIO.LOW)
Y2_PINS             = (GPIO.LOW, GPIO.HIGH, GPIO.LOW)

GPS_PINS = Y1_PINS
VHF_PINS = Y2_PINS


def init_pins():
    '''
    This is where we configure the uart. It's going to be doing multiple things:
    * controlling the two BOB-13906 UART mux boards
    * managing PTT and power settings for the Dorji DRA818 radio.
    *
    '''

    # cuz GPIO lib is noisy.
    GPIO.setwarnings(False)

    # We're going to use the Broadcom pin layout.
    GPIO.setmode(GPIO.BCM)

    # Radio initial pin values.
    GPIO.setup(VHF_PTT, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(VHF_HL, GPIO.OUT, initial=GPIO.LOW) # WARNING - Do NOT set this pin high.
    GPIO.setup(VHF_PD, GPIO.OUT, initial=GPIO.HIGH)

    # Transmit mux
    GPIO.setup(TX_MUX_E, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(TX_MUX_S0, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(TX_MUX_S1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(TX_MUX_S2, GPIO.OUT, initial=GPIO.LOW)

    # Receive mux
    GPIO.setup(RX_MUX_E, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(RX_MUX_S0, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(RX_MUX_S1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(RX_MUX_S2, GPIO.OUT, initial=GPIO.LOW)

    # Manually give power to the temperature sensor
    # This is a hack as I ran out of 3.3v rails. :(
    GPIO.setup(TEMP_VCC, GPIO.OUT, initial=GPIO.HIGH)

    # It's tempting, but please don't mess with the uart pins.
    # GPIO.setup(TX_MUX_Z, GPIO.OUT, initial=GPIO.LOW)
    # GPIO.setup(RX_MUX_Z, GPIO.IN, initial=GPIO.LOW)


def clear_uart():
    # fire up the E pin. This has the effect of disabling any
    # existing signal on the uart.
    GPIO.output(TX_MUX_E, GPIO.HIGH)
    GPIO.output(RX_MUX_E, GPIO.HIGH)

    # activate Y0. Leave E high.
    # we activate Y0 because it's not connected to any devices.
    mux_activate(*Y0_PINS, E=GPIO.HIGH)

def mux_activate(s0, s1, s2, E=GPIO.LOW):
    GPIO.output(TX_MUX_S0, s0)
    GPIO.output(TX_MUX_S1, s1)
    GPIO.output(TX_MUX_S2, s2)
    GPIO.output(RX_MUX_S0, s0)
    GPIO.output(RX_MUX_S1, s1)
    GPIO.output(RX_MUX_S2, s2)

    # do the E pins
    GPIO.output(TX_MUX_E, E)
    GPIO.output(RX_MUX_E, E)

# gps is Y1
def enable_gps():
    clear_uart()
    mux_activate(*GPS_PINS)

# vhf is Y2
def enable_vhf():
    clear_uart()
    mux_activate(*VHF_PINS)

def set_pin(pin, hilo):
    GPIO.output(pin, hilo)
