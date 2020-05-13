
#  the AX.25 frame
# 1 byte      : flag = b'\x7e'
# 7 bytes     : dest address, right padded, has a format
# 7 bytes     : source address, right padded, as a format
# 0-56 bytes  : digipeater addresses
# 1 byte      : control field = b'\x03'
# 1 byte      : protocol id = b'\xf0'
# 1-256 bytes : information field, format varies, but usually contains a header
# 2 bytes     : FCS checksum
# 1 byte      : flag, same as first.


FLAG = b'\x7e'
CTRL = b'\x03'
PCOL = b'\xf0'




