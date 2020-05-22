import serial
import time
import gpio
import logging

DEFAULT_UART_PORT = "/dev/ttyAMA0"

# default settings.
MODE = 1 # 1 = FM (5kHz deviation), 0 = NFM (2.5 kHz Deviation)
SQUELCH = 0 # Squelch Value, 0-8
CTCSS = '0000'

# pins
PTT     = 6
HL      = 13
PD      = 19

def _open_uart(device=DEFAULT_UART_PORT):
    return serial.Serial(
        port=device,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS)


def _send_rcv(uart, cmd, hang_time=1.00):
    logging.debug(f"=> {cmd.strip()}")
    uart.write(cmd.encode())
    time.sleep(hang_time)
    response = uart.readline()
    logging.debug(f"<= {response.decode('utf-8').strip()}")
    return response


def _handshake(uart):
    return _send_rcv(uart, "AT+DMOCONNECT\r\n")


def program(port=DEFAULT_UART_PORT, frequency=146.500, tries=4):
    ok = False
    while tries > 0 and not ok:
        tries -= 1
        try:
            uart = _open_uart(port)
            res = _handshake(uart).decode("utf-8").strip()
            if res != "+DMOCONNECT:0":
                logging.error("Unable to communicate with DRA818.")
            else:
                group_set_cmd = group_set_cmd = "AT+DMOSETGROUP=%d,%3.4f,%3.4f,%s,%d,%s\r\n" % (MODE, frequency, frequency, CTCSS, SQUELCH, CTCSS)
                res = _send_rcv(uart, group_set_cmd).decode('utf-8').strip()
                if res != "+DMOSETGROUP:0":
                    logging.error("Unable to program DRA818")
                else:
                    ok = True
        except:
            logging.waring(f"Programming VHF failed. {tries} tries left.")
        if not ok:
            time.sleep(0.5)
    return ok

def ptt(enabled):
    gpio.set_pin(PTT, gpio.LOW if enabled else gpio.HIGH)
