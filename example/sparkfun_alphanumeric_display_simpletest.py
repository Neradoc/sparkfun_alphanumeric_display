import board
import time
from sparkfun_alphanumeric_display import *

import displayio
displayio.release_displays()

# from digitalio import *
# button = DigitalInOut(board.BUTTON_SELECT)
# button.pull = Pull.DOWN

i2c = board.I2C()
# display = SparkFunQwiicDisplay(i2c, [0x70, 0x71])
display = SparkFunQwiicDisplay(i2c, 0x70)

display.blink_rate = 0
display.brightness = 1

while True:
    display.dot = 1
    for num in range(10000):
        display.print(f"{num:>4}")

    for num in range(len(SEGMENTS)):
        char = chr(num + 32)
        print(char, end="")
        display.print(char * 4)
        '''
        while button.value is True:
            time.sleep(0.01)
        while button.value is False:
            time.sleep(0.01)
        '''
        time.sleep(0.01)

    print("\n- dot", "-"*50)
    display.dot = True

    for num in range(len(SEGMENTS)):
        char = chr(num + 32)
        print(char, end="")
        display.print(char * 4)
        time.sleep(0.01)

    print("\n- colon", "-"*48)
    display.colon = True

    for num in range(len(SEGMENTS)):
        char = chr(num + 32)
        print(char, end="")
        display.print(char * 4)
        time.sleep(0.01)

    print("\n- none", "-"*49)
    display.dot = False
    display.colon = False
