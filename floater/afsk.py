import logging
import itertools
import math
from bitstring import BitArray, Bits
import audiogen
from audiogen.util import multiply
from audiogen.util import constant

logger = logging.getLogger(__name__)

"""
This is essentially a python 3 port of https://github.com/casebeer/afsk/blob/master/afsk/afsk.py
which is released under the BSD 2-Clause "Simplified" License found in  LICENSE_Casebeer.

I've modified it to use the bitstring library (was bitarray)
"""

MARK_HZ = 1200.0
SPACE_HZ = 2200.0
BAUD_RATE = 1200.0
TWO_PI = 2.0 * math.pi

def _as_bits(byte_data, mutable=True):
    should_convert = isinstance(byte_data, bytes) or isinstance(byte_data, bytearray)
    if should_convert:
        if mutable:
            return BitArray(byte_data)
        else:
            return Bits(byte_data)
    else:
        if mutable and byte_data.__class__.__name__ == 'Bits':
            return BitArray(byte_data)
        else:
            # technicaly, if they as for something non-mutable, we may return something mutable here.
            return byte_data

# bit generator
def nrzi(byte_data):
    '''
    Packet uses NRZI (non-return to zero inverted) encoding, which means
    that a 0 is encoded as a change in tone, and a 1 is encoded as
    no change in tone.
    '''
    cur = True
    for bit in _as_bits(byte_data):
        if not bit:
            cur = not cur
        yield cur

# technically a generator
def frame(byte_data):
    '''
    Frame data in 01111110 flag bytes and NRZI encode.
    Data must be already checksummed and stuffed. Frame will be
    preceded by two bytes of all zeros (which NRZI will encode as
    continuously altenrating tones) to assist with decoder clock
    sync.
    '''
    return nrzi((b'\x00' * 20) + (b'\x7e' * 100) + _as_bits(byte_data) + b'\x7e')

def modulate(byte_data):
    '''
    Generate Bell 202 AFSK samples for the given symbol generator
    Consumes raw wire symbols and produces the corresponding AFSK samples.
    '''
    seconds_per_sample = 1.0 / audiogen.sampler.FRAME_RATE
    phase, seconds, bits = 0, 0, 0

    # construct generators
    clock = (x / BAUD_RATE for x in itertools.count(1))
    tones = (MARK_HZ if bit else SPACE_HZ for bit in _as_bits(byte_data))

    for boundary, frequency in zip(clock, tones):
        # frequency of current symbol is determined by how much
        # we advance the signal's phase in each audio frame
        phase_change_per_sample = TWO_PI / (audiogen.sampler.FRAME_RATE / frequency)

        # produce samples for the current symbol
        # until we reach the next clock boundary
        while seconds < boundary:
            yield math.sin(phase)
            seconds += seconds_per_sample
            phase += phase_change_per_sample
            if phase > TWO_PI:
                phase -= TWO_PI
        bits += 1
        logger.debug(f"bits={bits}, time={(1000*seconds):.7}ms, expected time={(1000 * bits / BAUD_RATE):.7}ms, error={(1000 * (seconds - bits / BAUD_RATE)):.7}ms, baud rate ={(bits / seconds):.6} Hz")


def encode(byte_data):
    '''
    Encode binary data using Bell-202 AFSK

    Expects a bytes, bytearray, Bits or BitArray object of binary data as its argument.
    Returns a generator of sound samples suitable for use with the
    audiogen module.
    '''
    framed = frame(byte_data)

    # set volume to 1/2, preceed packet with 1/20 s silence to allow for startup glitches
    for sample in itertools.chain(
        audiogen.silence(1.05),
        multiply(modulate(framed), constant(0.5)),
        audiogen.silence(1.05)
    ):
        yield sample
