from adafruit_bus_device import i2c_device

SEGMENTS = [
    0b00000000000000, # ' ' (space)
    0b00001000001000, # '!'
    0b00001000000010, # '"'
    0b01001101001110, # '#'
    0b01001101101101, # '$'
    0b10010000100100, # '%'
    0b00110011011001, # '&'
    0b00001000000000, # '''
    0b00000000111001, # '('
    0b00000000001111, # ')'
    0b11111010000000, # '*'
    0b01001101000000, # '+'
    0b10000000000000, # ','
    0b00000101000000, # '-'
    0b00000000000000, # '.'
    0b10010000000000, # '/'
    0b00000000111111, # '0'
    0b00010000000110, # '1'
    0b00000101011011, # '2'
    0b00000101001111, # '3'
    0b00000101100110, # '4'
    0b00000101101101, # '5'
    0b00000101111101, # '6'
    0b01010000000001, # '7'
    0b00000101111111, # '8'
    0b00000101100111, # '9'
    0b00000000000000, # ':'
    0b10001000000000, # ';'
    0b00110000000000, # '<'
    0b00000101001000, # '='
    0b01000010000000, # '>'
    0b01000100000011, # '?'
    0b00001100111011, # '@'
    0b00000101110111, # 'A'
    0b01001100001111, # 'B'
    0b00000000111001, # 'C'
    0b01001000001111, # 'D'
    0b00000101111001, # 'E'
    0b00000101110001, # 'F'
    0b00000100111101, # 'G'
    0b00000101110110, # 'H'
    0b01001000001001, # 'I'
    0b00000000011110, # 'J'
    0b00110001110000, # 'K'
    0b00000000111000, # 'L'
    0b00010010110110, # 'M'
    0b00100010110110, # 'N'
    0b00000000111111, # 'O'
    0b00000101110011, # 'P'
    0b00100000111111, # 'Q'
    0b00100101110011, # 'R'
    0b00000110001101, # 'S'
    0b01001000000001, # 'T'
    0b00000000111110, # 'U'
    0b10010000110000, # 'V'
    0b10100000110110, # 'W'
    0b10110010000000, # 'X'
    0b01010010000000, # 'Y'
    0b10010000001001, # 'Z'
    0b00000000111001, # '['
    0b00100010000000, # '\'
    0b00000000001111, # ']'
    0b10100000000000, # '^'
    0b00000000001000, # '_'
    0b00000010000000, # '`'
    0b00000101011111, # 'a'
    0b00100001111000, # 'b'
    0b00000101011000, # 'c'
    0b10000100001110, # 'd'
    0b00000001111001, # 'e'
    0b00000001110001, # 'f'
    0b00000110001111, # 'g'
    0b00000101110100, # 'h'
    0b01000000000000, # 'i'
    0b00000000001110, # 'j'
    0b01111000000000, # 'k'
    0b01001000000000, # 'l'
    0b01000101010100, # 'm'
    0b00100001010000, # 'n'
    0b00000101011100, # 'o'
    0b00010001110001, # 'p'
    0b00100101100011, # 'q'
    0b00000001010000, # 'r'
    0b00000110001101, # 's'
    0b00000001111000, # 't'
    0b00000000011100, # 'u'
    0b10000000010000, # 'v'
    0b10100000010100, # 'w'
    0b10110010000000, # 'x'
    0b00001100001110, # 'y'
    0b10010000001001, # 'z'
    0b10000011001001, # '{'
    0b01001000000000, # '|'
    0b00110100001001, # '}'
    0b00000101010010, # '~'
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
    def __init__(self, i2c, address=0x70):
        self.device = i2c_device.I2CDevice(i2c, address)
        self._duty = 15
        self._blink_rate = ALPHA_BLINK_RATE_NOBLINK
        self.setup()

    @property
    def brightness(self):
        return self._duty

    @brightness.setter
    def brightness(self, brightness):
        self._duty = brightness & 0xF

    @property
    def blink_rate(self):
        raise NotImplementedError()
        return self._blink_rate

    @blink_rate.setter
    def blink_rate(self, blink_rate):
        raise NotImplementedError()
        self._blink_rate = ALPHA_BLINK_RATE_NOBLINK

    def setup(self):
        with self.device as bus:
            bus.write(bytes([ENABLE_SYS_CLOCK]))
            bus.write(bytes([ALPHA_CMD_DIMMING_SETUP | (self._duty & 0xF)]))
            command = (
                ALPHA_CMD_DISPLAY_SETUP
                | (self._blink_rate << 1)
                | ALPHA_DISPLAY_ON
            )
            bus.write(bytes([command]))

    def show_letter(self, char):
        buffer = bytearray(16)
        segment = SEGMENTS[ord(char) - ord(" ")]
        for i in range(8):
            pos = i * 2
            buffer[pos] = (segment >> i) & 1 | ((segment >> (i + 8)) & 1) * 0x10
        print(buffer)
        with self.device as bus:
            bus.write(b"\x00" + bytes(buffer))
