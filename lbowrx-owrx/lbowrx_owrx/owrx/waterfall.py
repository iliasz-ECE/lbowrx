from owrx.form.input import DropdownEnum
from owrx.config import Config


class Waterfall(object):
    def __init__(self, colors):
        self.colors = colors

    def getColors(self):
        return self.colors


class GoogleTurboWaterfall(Waterfall):
    def __init__(self):
        super().__init__(
            [
                0x30123B,
                0x311542,
                0x33184A,
                0x341B51,
                0x351E58,
                0x36215F,
                0x372466,
                0x38266C,
                0x392973,
                0x3A2C79,
                0x3B2F80,
                0x3C3286,
                0x3D358B,
                0x3E3891,
                0x3E3A97,
                0x3F3D9C,
                0x4040A2,
                0x4043A7,
                0x4146AC,
                0x4248B1,
                0x424BB6,
                0x434EBA,
                0x4351BF,
                0x4453C3,
                0x4456C7,
                0x4559CB,
                0x455BCF,
                0x455ED3,
                0x4561D7,
                0x4663DA,
                0x4666DD,
                0x4669E1,
                0x466BE4,
                0x466EE7,
                0x4671E9,
                0x4673EC,
                0x4676EE,
                0x4678F1,
                0x467BF3,
                0x467DF5,
                0x4680F7,
                0x4682F9,
                0x4685FA,
                0x4587FC,
                0x458AFD,
                0x448CFE,
                0x448FFE,
                0x4391FF,
                0x4294FF,
                0x4196FF,
                0x3F99FF,
                0x3E9BFF,
                0x3D9EFE,
                0x3BA1FD,
                0x3AA3FD,
                0x38A6FB,
                0x36A8FA,
                0x35ABF9,
                0x33ADF7,
                0x31B0F6,
                0x2FB2F4,
                0x2DB5F2,
                0x2CB7F0,
                0x2AB9EE,
                0x28BCEC,
                0x26BEEA,
                0x25C0E7,
                0x23C3E5,
                0x21C5E2,
                0x20C7E0,
                0x1FC9DD,
                0x1DCCDB,
                0x1CCED8,
                0x1BD0D5,
                0x1AD2D3,
                0x19D4D0,
                0x18D6CD,
                0x18D8CB,
                0x18DAC8,
                0x17DBC5,
                0x17DDC3,
                0x17DFC0,
                0x18E0BE,
                0x18E2BB,
                0x19E3B9,
                0x1AE5B7,
                0x1BE6B4,
                0x1DE8B2,
                0x1EE9AF,
                0x20EAAD,
                0x22ECAA,
                0x24EDA7,
                0x27EEA4,
                0x29EFA1,
                0x2CF09E,
                0x2FF19B,
                0x32F298,
                0x35F394,
                0x38F491,
                0x3CF58E,
                0x3FF68B,
                0x43F787,
                0x46F884,
                0x4AF980,
                0x4EFA7D,
                0x51FA79,
                0x55FB76,
                0x59FC73,
                0x5DFC6F,
                0x61FD6C,
                0x65FD69,
                0x69FE65,
                0x6DFE62,
                0x71FE5F,
                0x75FF5C,
                0x79FF59,
                0x7DFF56,
                0x80FF53,
                0x84FF50,
                0x88FF4E,
                0x8BFF4B,
                0x8FFF49,
                0x92FF46,
                0x96FF44,
                0x99FF42,
                0x9CFE40,
                0x9FFE3E,
                0xA2FD3D,
                0xA4FD3B,
                0xA7FC3A,
                0xAAFC39,
                0xACFB38,
                0xAFFA37,
                0xB1F936,
                0xB4F835,
                0xB7F835,
                0xB9F634,
                0xBCF534,
                0xBFF434,
                0xC1F334,
                0xC4F233,
                0xC6F033,
                0xC9EF34,
                0xCBEE34,
                0xCEEC34,
                0xD0EB34,
                0xD2E934,
                0xD5E835,
                0xD7E635,
                0xD9E435,
                0xDBE236,
                0xDDE136,
                0xE0DF37,
                0xE2DD37,
                0xE4DB38,
                0xE6D938,
                0xE7D738,
                0xE9D539,
                0xEBD339,
                0xEDD139,
                0xEECF3A,
                0xF0CD3A,
                0xF1CB3A,
                0xF3C93A,
                0xF4C73A,
                0xF5C53A,
                0xF7C33A,
                0xF8C13A,
                0xF9BF39,
                0xFABD39,
                0xFABA38,
                0xFBB838,
                0xFCB637,
                0xFCB436,
                0xFDB135,
                0xFDAF35,
                0xFEAC34,
                0xFEA933,
                0xFEA732,
                0xFEA431,
                0xFFA12F,
                0xFF9E2E,
                0xFF9C2D,
                0xFF992C,
                0xFE962B,
                0xFE932A,
                0xFE9028,
                0xFE8D27,
                0xFD8A26,
                0xFD8724,
                0xFC8423,
                0xFC8122,
                0xFB7E20,
                0xFB7B1F,
                0xFA781E,
                0xF9751C,
                0xF8721B,
                0xF86F1A,
                0xF76C19,
                0xF66917,
                0xF56616,
                0xF46315,
                0xF36014,
                0xF25D13,
                0xF05B11,
                0xEF5810,
                0xEE550F,
                0xED530E,
                0xEB500E,
                0xEA4E0D,
                0xE94B0C,
                0xE7490B,
                0xE6470A,
                0xE4450A,
                0xE34209,
                0xE14009,
                0xDF3E08,
                0xDE3C07,
                0xDC3A07,
                0xDA3806,
                0xD83606,
                0xD63405,
                0xD43205,
                0xD23105,
                0xD02F04,
                0xCE2D04,
                0xCC2B03,
                0xCA2903,
                0xC82803,
                0xC62602,
                0xC32402,
                0xC12302,
                0xBF2102,
                0xBC1F01,
                0xBA1E01,
                0xB71C01,
                0xB41B01,
                0xB21901,
                0xAF1801,
                0xAC1601,
                0xAA1501,
                0xA71401,
                0xA41201,
                0xA11101,
                0x9E1001,
                0x9B0F01,
                0x980D01,
                0x950C01,
                0x920B01,
                0x8E0A01,
                0x8B0901,
                0x880801,
                0x850701,
                0x810602,
                0x7E0502,
                0x7A0402,
            ]
        )


class TeejeezWaterfall(Waterfall):
    def __init__(self):
        super().__init__([0x000000, 0x0000FF, 0x00FFFF, 0x00FF00, 0xFFFF00, 0xFF0000, 0xFF00FF, 0xFFFFFF])


class Ha7ilmWaterfall(Waterfall):
    def __init__(self):
        super().__init__([0x000000, 0x2E6893, 0x69A5D0, 0x214B69, 0x9DC4E0, 0xFFF775, 0xFF8A8A, 0xB20000])


class CustomWaterfall(Waterfall):
    def __init__(self):
        config = Config.get()
        if "waterfall_colors" in config and config["waterfall_colors"]:
            colors = config["waterfall_colors"]
        else:
            # fallback: black and white
            colors = [0x000000, 0xffffff]
        super().__init__(colors)


class WaterfallOptions(DropdownEnum):
    DEFAULT = ("Google Turbo (OpenWebRX default)", GoogleTurboWaterfall)
    TEEJEEZ = ("Original colorscheme by teejeez (default in OpenWebRX < 0.20)", TeejeezWaterfall)
    HA7ILM = ("Old theme by HA7ILM", Ha7ilmWaterfall)
    CUSTOM = ("Custom", CustomWaterfall)

    def __new__(cls, *args, **kwargs):
        description, waterfallClass = args
        obj = object.__new__(cls)
        obj._value_ = waterfallClass.__name__
        obj.waterfallClass = waterfallClass
        obj.description = description
        return obj

    def __str__(self):
        return self.description

    def instantiate(self):
        return self.waterfallClass()

    @staticmethod
    def findByColors(colors):
        for o in WaterfallOptions:
            if o is WaterfallOptions.CUSTOM:
                continue
            waterfall = o.instantiate()
            if waterfall.getColors() == colors:
                return o
        return WaterfallOptions.CUSTOM
