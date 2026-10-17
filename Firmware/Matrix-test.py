"""
Standalone key-matrix test (no KMK needed).

Copy this to CIRCUITPY as code.py (temporarily), open the serial console
(for example with the Mu editor or `screen /dev/tty.usbmodem*`) and press each
key. It should print the switch name you pressed, e.g. "SW5 pressed".

If a key prints the wrong name, or two keys print the same name, check the
column and row nets on the PCB for that switch and its diode.
"""

import time

import board
import digitalio

COLS = (board.D2, board.D3, board.D4, board.D5)  # COL1..COL4
ROWS = (board.D0, board.D1)  # ROW1, ROW2

# NAMES[row][col]
NAMES = (
    ("SW1", "SW3", "SW5", "SW7"),  # ROW1 (top)
    ("SW2", "SW4", "SW6", "SW8"),  # ROW2 (bottom)
)

cols = []
for pin in COLS:
    io = digitalio.DigitalInOut(pin)
    io.direction = digitalio.Direction.OUTPUT
    io.value = False
    cols.append(io)

rows = []
for pin in ROWS:
    io = digitalio.DigitalInOut(pin)
    io.direction = digitalio.Direction.INPUT
    io.pull = digitalio.Pull.DOWN
    rows.append(io)

previous = set()
print("Matrix test running. Press keys...")

while True:
    pressed = set()
    for c, col in enumerate(cols):
        col.value = True  # COL2ROW: drive the column, read the rows
        time.sleep(0.0005)
        for r, row in enumerate(rows):
            if row.value:
                pressed.add(NAMES[r][c])
        col.value = False

    for name in sorted(pressed - previous):
        print(name, "pressed")
    for name in sorted(previous - pressed):
        print(name, "released")
    previous = pressed
    time.sleep(0.01)Matrix test · PY
