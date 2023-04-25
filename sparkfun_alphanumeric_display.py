from adafruit_bus_device import i2c_device
from micropython import const
import time

SEGMENTS = [
    # NMLKJIHGFEDCBA
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

BLINK_RATE_NOBLINK = 0b00
BLINK_RATE_2HZ = 0b01
BLINK_RATE_1HZ = 0b10
BLINK_RATE_0_5HZ = 0b11

_CMD_DISPLAY_SETUP = const(0b10000000)
_CMD_DIMMING_SETUP = const(0b11100000)
_CMD_SYSTEM_SETUP = const(0b00100000)
_ENABLE_SYS_CLOCK = const(_CMD_SYSTEM_SETUP | 1)

"""
The first digit is encoded in the first bit of each nymble used
The second is encoded in the recond bit, etc.

S: semicolon
P: dot

      A
     ---
  F |IJK| B
    -G-H-
  E |NML| C
     ---
      D

#  HA    _S    IB    _P    JC    __    KD    __
 0x11, 0x01, 0x11, 0x01, 0x11, 0x00, 0x11, 0x11,
#  LE    __    MF    __    NG    __    __    __
 0x11, 0x00, 0x11, 0x00, 0x11, 0x00, 0x00, 0x00,
"""

class SparkFunQwiicDisplay:
    def __init__(self, i2c, address=0x70, brightness=0xF, auto_write=True):
        if isinstance(address, int):
            address = [address]
        self.devices = []
        for addr in address:
            self.devices.append(i2c_device.I2CDevice(i2c, addr))
        self.auto_write = auto_write
        self._duty = 15
        self._blink_rate = BLINK_RATE_NOBLINK
        self._duty = brightness & 0xF
        self._display_on = True
        self._colon = 0
        self._dot = 0
        self._text = ""
        self._buffer = bytearray(17)
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
        """A value from 0 to 3. From no blink to the faster blink rate."""
        return self._blink_rate

    @blink_rate.setter
    def blink_rate(self, blink_rate):
        blink_rate = blink_rate & 0b11
        if blink_rate:
            self._blink_rate = 0b100 - blink_rate
        else:
            self._blink_rate = BLINK_RATE_NOBLINK
        self.setup()

    @property
    def colon(self):
        """
        Bitmask of which displays have a semicolon.
        Use  1 << devnum. One display, show colon: 1.
        Three displays, colon on the last one: 0b100.
        """
        return self._colon

    @colon.setter
    def colon(self, value:int):
        self._colon = value
        self.show()

    @property
    def dot(self):
        """
        Bitmask of which displays have a dot.
        Use  1 << devnum. One display, show dot: 1.
        Three displays, dot on the last one: 0b100.
        """
        return self._dot

    @dot.setter
    def dot(self, value:int):
        self._dot = value
        self.show()

    def setup(self):
        """Setup the display, brightness and blink base on current config."""
        for device in self.devices:
            with device as bus:
                bus.write(bytes([_ENABLE_SYS_CLOCK]))
                bus.write(bytes([_CMD_DIMMING_SETUP | (self._duty & 0xF)]))
                command = (
                    _CMD_DISPLAY_SETUP
                    | (self._blink_rate << 1)
                    | int(self._display_on)
                )
                bus.write(bytes([command]))

    def show(self):
        """Update the display with the current text."""
        buffer = self._buffer
        for devnum, device in enumerate(self.devices):
            # erase the character buffer
            for i in range(7):
                buffer[2 * i + 1] = 0
            # set bits for each character
            for pos, char in enumerate(self._text[devnum * 4:devnum * 4 + 4]):
                segment = SEGMENTS[ord(char) - ord(" ")]
                for i in range(7):
                    digit = (segment >> i) & 1
                    digit |= ((segment >> (i + 7)) & 1) << 4
                    buffer[1 + i * 2] |= digit * (1 << pos)
            buffer[2] = (self._colon >> devnum) & 1
            buffer[4] = (self._dot >> devnum) & 1
            #
            with device as bus:
                bus.write(buffer)

    def print(self, text):
        """Print the string to the display from left to right."""
        self._text = text
        if self.auto_write:
            self.show()
