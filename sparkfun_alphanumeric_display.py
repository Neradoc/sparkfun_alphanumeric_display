from adafruit_bus_device import i2c_device

SEGMENTS = [
    0b00000000000000, # ' ' (space)
    0b00001000001000, # '!'
    0b00001000000010, # '"'
    0b01001011001110, # '#'
    0b01001011101101, # '$'
    0b10010000100100, # '%'
    0b00110101011001, # '&'
    0b00001000000000, # '''
    0b00000000111001, # '('
    0b00000000001111, # ')'
    0b11111100000000, # '*'
    0b01001011000000, # '+'
    0b10000000000000, # ','
    0b00000011000000, # '-'
    0b00000000000000, # '.'
    0b10010000000000, # '/'
    0b00000000111111, # '0'
    0b00010000000110, # '1'
    0b00000011011011, # '2'
    0b00000011001111, # '3'
    0b00000011100110, # '4'
    0b00000011101101, # '5'
    0b00000011111101, # '6'
    0b01010000000001, # '7'
    0b00000011111111, # '8'
    0b00000011100111, # '9'
    0b00000000000000, # ':'
    0b10001000000000, # ';'
    0b00110000000000, # '<'
    0b00000011001000, # '='
    0b10000100000000, # '>'
    0b01000010000011, # '?'
    0b00001010111011, # '@'
    0b00000011110111, # 'A'
    0b01001010001111, # 'B'
    0b00000000111001, # 'C'
    0b01001000001111, # 'D'
    0b00000011111001, # 'E'
    0b00000011110001, # 'F'
    0b00000010111101, # 'G'
    0b00000011110110, # 'H'
    0b01001000001001, # 'I'
    0b00000000011110, # 'J'
    0b00110001110000, # 'K'
    0b00000000111000, # 'L'
    0b00010100110110, # 'M'
    0b00100100110110, # 'N'
    0b00000000111111, # 'O'
    0b00000011110011, # 'P'
    0b00100000111111, # 'Q'
    0b00100011110011, # 'R'
    0b00000110001101, # 'S'
    0b01001000000001, # 'T'
    0b00000000111110, # 'U'
    0b10010000110000, # 'V'
    0b10100000110110, # 'W'
    0b10110100000000, # 'X'
    0b01010100000000, # 'Y'
    0b10010000001001, # 'Z'
    0b00000000111001, # '['
    0b00100100000000, # '\'
    0b00000000001111, # ']'
    0b10100000000000, # '^'
    0b00000000001000, # '_'
    0b00000100000000, # '`'
    0b00000011011111, # 'a'
    0b00100001111000, # 'b'
    0b00000011011000, # 'c'
    0b10000010001110, # 'd'
    0b00000001111001, # 'e'
    0b00000001110001, # 'f'
    0b00000110001111, # 'g'
    0b00000011110100, # 'h'
    0b01000000000000, # 'i'
    0b00000000001110, # 'j'
    0b01111000000000, # 'k'
    0b01001000000000, # 'l'
    0b01000011010100, # 'm'
    0b00100001010000, # 'n'
    0b00000011011100, # 'o'
    0b00010001110001, # 'p'
    0b00100011100011, # 'q'
    0b00000001010000, # 'r'
    0b00000110001101, # 's'
    0b00000001111000, # 't'
    0b00000000011100, # 'u'
    0b10000000010000, # 'v'
    0b10100000010100, # 'w'
    0b10110100000000, # 'x'
    0b00001010001110, # 'y'
    0b10010000001001, # 'z'
    0b10000101001001, # '{'
    0b01001000000000, # '|'
    0b00110010001001, # '}'
    0b00000011010010, # '~'
    0b11111111111111, # Unknown character (DEL or RUBOUT)
]

ALPHA_BLINK_RATE_NOBLINK = 0b00
ALPHA_BLINK_RATE_2HZ = 0b01
ALPHA_BLINK_RATE_1HZ = 0b10
ALPHA_BLINK_RATE_0_5HZ = 0b11

ALPHA_CMD_SYSTEM_SETUP = 0b00100000
ALPHA_CMD_DISPLAY_SETUP = 0b10000000
ALPHA_CMD_DIMMING_SETUP = 0b11100000

ALPHA_DISPLAY_ON = 0b1
ALPHA_DISPLAY_OFF = 0b0

ENABLE_SYS_CLOCK = ALPHA_CMD_SYSTEM_SETUP | 1

"""
//  S: semicolon
//  P: dot
//
//      A
//     ---
//  F |IJK| B
//    -GH--
//  E |LMN| C
//     ---
//      D
"""
buffer0 = bytearray(
    #  HA    _S    IB    _P    JC    __    KD    __
    [0x11, 0x01, 0x11, 0x01, 0x11, 0x00, 0x11, 0x11]+
    #  NE    __    MF    __    LG    __    __    __
    [0x11, 0x00, 0x11, 0x00, 0x11, 0x00, 0x00, 0x00]
)

class SparkFunQwiicDisplay:
    def __init__(self, i2c, address=0x70, brightness=0xF):
        self.device = i2c_device.I2CDevice(i2c, address)
        self._duty = 15
        self._blink_rate = ALPHA_BLINK_RATE_NOBLINK
        self._duty = brightness & 0xF
        self._display_on = True
        self._colon = False
        self._dot = False
        self._text = ""
        self.setup()

    @property
    def brightness(self):
        """
        Brightness is a value between 0 and 15.
        Set to None in order to turn off the display.
        """
        return self._duty

    @brightness.setter
    def brightness(self, brightness):
        if brightness is None:
            self._display_on = False
            self.setup()
        else:
            self._display_on = True
            self._duty = brightness & 0xF
            self.setup()

    @property
    def blink_rate(self):
        return self._blink_rate

    @blink_rate.setter
    def blink_rate(self, blink_rate):
        blink_rate = blink_rate & 0b11
        if blink_rate:
            self._blink_rate = 0b100 - blink_rate
        else:
            self._blink_rate = ALPHA_BLINK_RATE_NOBLINK
        self.setup()

    @property
    def colon(self):
        return self._colon

    @colon.setter
    def colon(self, on):
        self._colon = bool(on)
        self.refresh()

    @property
    def dot(self):
        return self._dot

    @dot.setter
    def dot(self, on):
        self._dot = bool(on)
        self.refresh()

    def setup(self):
        with self.device as bus:
            bus.write(bytes([ENABLE_SYS_CLOCK]))
            bus.write(bytes([ALPHA_CMD_DIMMING_SETUP | (self._duty & 0xF)]))
            command = (
                ALPHA_CMD_DISPLAY_SETUP
                | (self._blink_rate << 1)
                | int(self._display_on)
            )
            bus.write(bytes([command]))

    def refresh(self):
        self.print(self._text)

    def print(self, text):
        self._text = text
        buffer = bytearray(16)
        for pos, char in enumerate(text[:4]):
            segment = SEGMENTS[ord(char) - ord(" ")]
            for i in range(7):
                digit = (segment >> i) & 1
                digit |= ((segment >> (i + 7)) & 1) << 4
                buffer[i * 2] |= digit * (1 << pos)
            if pos == 0:
                if self._colon:
                    buffer[1] |= 1
                if self._dot:
                    buffer[3] |= 1
        with self.device as bus:
            bus.write(b"\x00" + bytes(buffer))
