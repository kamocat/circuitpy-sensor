# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
"""CircuitPython I2C Device Address Scan"""
import time
import board
import busio
import digitalio

pin = digitalio.DigitalInOut(board.GP17)  # Used here to control the bmp280 I2C address
pin.direction = digitalio.Direction.OUTPUT
pin.value = True

i2c = busio.I2C(board.GP19, board.GP18)  # SCL, SDA

while not i2c.try_lock():
    pass

try:
    while True:
        print(
            "I2C addresses found:",
            [hex(device_address) for device_address in i2c.scan()],
        )
        time.sleep(2)

finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
    i2c.unlock()
