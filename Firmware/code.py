"""
Macropad firmware: KMK on CircuitPython, for a Seeed XIAO RP2040.

Hardware (see README.md for the full pin map):
  * 8 MX-style switches in a 2 x 4 matrix, one 1N4148W diode per switch
  * Diodes have the cathode (bar) towards the ROW, so the matrix is COL2ROW
  * 3.5" ILI9488 SPI display on the XIAO's SPI pins (optional, see screen.py)


"""

import board

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation

# ---------------------------------------------------------------------------
# Settings you may want to change
# ---------------------------------------------------------------------------

# Shortcut modifier: Cmd on macOS, Ctrl on Windows/Linux.
USE_MAC = True
MOD = KC.LGUI if USE_MAC else KC.LCTL

# Show a key legend on the display. If the display is not fitted, or fails to
# start, the keys still work.
ENABLE_DISPLAY = True

# ---------------------------------------------------------------------------
# Matrix
# ---------------------------------------------------------------------------

keyboard = KMKKeyboard()

# XIAO RP2040 pins, matching the schematic nets:
#   COL1..COL4 -> XIAO pads 3..6  (D2, D3, D4, D5)
#   ROW1, ROW2 -> XIAO pads 1, 2  (D0, D1)
keyboard.col_pins = (board.D2, board.D3, board.D4, board.D5)
keyboard.row_pins = (board.D0, board.D1)

# Diode cathode (bar) faces the row, anode faces the switch.
keyboard.diode_orientation = DiodeOrientation.COL2ROW

# ---------------------------------------------------------------------------
# Keymap
# ---------------------------------------------------------------------------
# Physical layout on the PCB (and the order the keys are listed below):
#
#   top row    (ROW1):  SW1  SW3  SW5  SW7
#   bottom row (ROW2):  SW2  SW4  SW6  SW8
#
# KMK numbers keys row by row, so the first four entries are the top row and
# the next four are the bottom row.

LABELS = (
    "Copy", "Paste", "Cut", "Undo",
    "Save", "All", "Find", "Tab",
)

keyboard.keymap = [
    [
        MOD(KC.C), MOD(KC.V), MOD(KC.X), MOD(KC.Z),
        MOD(KC.S), MOD(KC.A), MOD(KC.F), MOD(KC.T),
    ]
]

# ---------------------------------------------------------------------------
# Display (optional)
# ---------------------------------------------------------------------------

if ENABLE_DISPLAY:
    try:
        import screen

        screen.show_legend(LABELS, title="MACROPAD", cols=4)
    except Exception as err:  # keep the keyboard working whatever happens
        print("Display disabled:", err)

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    keyboard.go()
