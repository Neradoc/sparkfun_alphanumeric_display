import board
import time
from sparkfun_alphanumeric_display import SparkFunQwiicDisplay

i2c = board.I2C()
display = SparkFunQwiicDisplay(i2c)

while True:
    for char in "11111 77777 ":
        display.show_letter(char)
        time.sleep(0.3)

for num in range(32):
    char = chr(num + 32)
    display.show_letter(char)
    time.sleep(0.1)

# value = 0
# for i in range(8*16):
#     value = value | (1 << i)
#     data = value.to_bytes(16, "little")
#     print(i, bin(i), data)
#     bus.write(b"\x00" + data)
#     time.sleep(0.01)
