import logging

BCM=0
OUT=1
IN=2
HIGH=3
LOW=4


def _const_tos(c):
    m = {
        BCM: "BCM",
        OUT: "OUT",
        IN: "IN",
        HIGH: "HIGH",
        LOW: "LOW"
    }
    return m.get(c, f"INVALID {c}")


def setmode(board_mode):
    logging.debug(f"Setting GPIO board mode to {_const_tos(board_mode)}")


def setup(pin_num, io_mode, initial=LOW):
    logging.debug(f"pin {pin_num} mode {_const_tos(io_mode)} value {_const_tos(initial)}")


def output(pin_num, hilo):
    logging.debug(f"pin {pin_num} set {_const_tos(hilo)}")