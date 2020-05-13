
class MsgCodes(object):
    MO = ("M0", "Off Duty", "111")
    M1 = ("M1", "En Route", "110")
    M2 = ("M2", "In Service", "101")
    M3 = ("M3", "Returning", "100")
    M4 = ("M4", "Committed", "011")
    M5 = ("M5", "Special", "010")
    M6 = ("M6", "Priority", "001")
    C0 = ("C0", "Custom-0", "111")
    C1 = ("C1", "Custom-1", "110")
    C2 = ("C2", "Custom-2", "101")
    C3 = ("C3", "Custom-3", "100")
    C4 = ("C4", "Custom-4", "011")
    C5 = ("C5", "Custom-5", "010")
    C6 = ("C6", "Custom-6", "001")
    EM = (None, "Emergency", "000")

class SSID(object):
    ID_0 = ('0', 'Use VIA Path')
    ID_1 = ('1', 'WIDE1-1')
    ID_2 = ('2', 'WIDE2-2')
    ID_3 = ('3', 'WIDE3-3')
    ID_4 = ('4', 'WIDE4-4')
    ID_5 = ('5', 'WIDE5-5')
    ID_6 = ('6', 'WIDE6-6')
    ID_7 = ('7', 'WIDE7-7')
    ID_8 = ('8', 'North path')
    ID_9 = ('9', 'South path')
    ID_10 = ('10', 'East path')
    ID_11 = ('11', 'West path')
    ID_12 = ('12', 'North path + WIDE')
    ID_13 = ('13', 'South path + WIDE')
    ID_14 = ('14', 'East path + WIDE')
    ID_15 = ('15', 'West path + WIDE')

    @staticmethod
    def normalize(key_or_tuple):
        key = None
        if isinstance(key_or_tuple, tuple):
            key = key_or_tuple[0]
        elif isinstance(key_or_tuple, int):
            key = str(key_or_tuple)
        else:
            raise RuntimeError(f"Unexpected reference: {key_or_tuple}")
        return {
            '0': SSID.ID_0,
            '1': SSID.ID_1,
            '2': SSID.ID_2,
            '3': SSID.ID_3,
            '4': SSID.ID_4,
            '5': SSID.ID_5,
            '6': SSID.ID_6,
            '7': SSID.ID_7,
            '8': SSID.ID_8,
            '9': SSID.ID_9,
            '10': SSID.ID_10,
            '11': SSID.ID_11,
            '12': SSID.ID_12,
            '13': SSID.ID_13,
            '14': SSID.ID_14,
            '15': SSID.ID_15
        }[key]