"""
Display support for the 3.5" ILI9488 SPI module (480 x 320, landscape).

Wiring, from the schematic:
    SCK         -> XIAO D8  (GP2, SPI0 SCK)
    MOSI        -> XIAO D10 (GP3, SPI0 TX)
    MISO        -> XIAO D9  (GP4)  not used, the screen is write-only here
    SCREEN_CS   -> XIAO D6  (GP0)
    SCREEN_DC   -> XIAO D7  (GP1)
    RESET       -> tied to 3V3 on the PCB, so a software reset is sent instead
    LED         -> tied to 3V3 on the PCB, so the backlight is always on

Libraries needed in CIRCUITPY/lib:
    adafruit_display_text   (from the Adafruit CircuitPython Bundle)

IMPORTANT: this has not been tested on hardware. The ILI9488 officially only
accepts 18-bit colour over 4-wire SPI, while CircuitPython's displayio sends
16-bit pixels. Many modules tolerate that, some do not. If the screen stays
white or shows garbage, the keys are unaffected (code.py catches the error or
simply carries on); see README.md for options.
"""

import board
import busio
import displayio
import terminalio
import vectorio

# CircuitPython 9+ moved these classes; older versions keep them in displayio.
try:
    from fourwire import FourWire
    from busdisplay import BusDisplay as _Display
except ImportError:
    from displayio import FourWire
    from displayio import Display as _Display

WIDTH = 480
HEIGHT = 320

# COLMOD (0x3A) pixel format: 0x55 = 16 bit (what displayio sends).
# Change to 0x66 only if you also use a driver that sends 18-bit pixels.
COLMOD = b"\x55"

# MADCTL (0x36): 0x28 = landscape + BGR order. Try 0xE8 if the image is
# upside down, 0x68 or 0xA8 if it is mirrored.
MADCTL = b"\x28"

# displayio init sequence: command, (data length | 0x80 if a delay follows),
# data bytes, then the delay in ms (when flagged).
_INIT_SEQUENCE = (
    b"\x01\x80\x96"  # software reset, wait 150 ms (RESET pin is tied high)
    b"\x11\x80\x78"  # sleep out, wait 120 ms
    b"\xe0\x0f\x00\x03\x09\x08\x16\x0a\x3f\x78\x4c\x09\x0a\x08\x16\x1a\x0f"  # + gamma
    b"\xe1\x0f\x00\x16\x19\x03\x0f\x05\x32\x45\x46\x04\x0e\x0d\x35\x37\x0f"  # - gamma
    b"\xc0\x02\x17\x15"  # power control 1
    b"\xc1\x01\x41"  # power control 2
    b"\xc5\x03\x00\x12\x80"  # VCOM
    b"\x36\x01" + MADCTL +  # memory access control
    b"\x3a\x01" + COLMOD +  # pixel format
    b"\xb0\x01\x00"  # interface mode control
    b"\xb1\x01\xa0"  # frame rate
    b"\xb4\x01\x02"  # display inversion control
    b"\xb6\x03\x02\x02\x3b"  # display function control
    b"\xe9\x01\x00"  # set image function
    b"\xf7\x04\xa9\x51\x2c\x82"  # adjust control 3
    b"\x29\x80\x78"  # display on, wait 120 ms
)

_BG = 0x101018
_CELL = 0x2A2A44
_TEXT = 0xF0F0F0
_TITLE = 0x6FD3FF


def _rect(x, y, w, h, colour):
    palette = displayio.Palette(1)
    palette[0] = colour
    return vectorio.Rectangle(pixel_shader=palette, width=w, height=h, x=x, y=y)


def show_legend(labels, title="MACROPAD", cols=4):
    """Draw a title and a grid showing what each key does.

    `labels` is listed in KMK key order (row by row), so it matches the
    physical layout of the keys on the board.
    """
    from adafruit_display_text import label

    displayio.release_displays()

    spi = busio.SPI(board.SCK, MOSI=board.MOSI)  # MISO unused
    bus = FourWire(
        spi,
        command=board.D7,  # SCREEN_DC
        chip_select=board.D6,  # SCREEN_CS
        reset=None,  # tied to 3V3 on the PCB
        baudrate=16_000_000,
    )
    display = _Display(
        bus,
        _INIT_SEQUENCE,
        width=WIDTH,
        height=HEIGHT,
        rotation=0,
        auto_refresh=False,
    )

    root = displayio.Group()
    root.append(_rect(0, 0, WIDTH, HEIGHT, _BG))

    root.append(
        label.Label(
            terminalio.FONT,
            text=title,
            color=_TITLE,
            scale=3,
            anchor_point=(0.5, 0.5),
            anchored_position=(WIDTH // 2, 32),
        )
    )

    rows = (len(labels) + cols - 1) // cols
    margin = 16
    top = 72
    cell_w = (WIDTH - margin * (cols + 1)) // cols
    cell_h = (HEIGHT - top - margin * (rows + 1) + margin) // rows

    for index, text in enumerate(labels):
        row, col = divmod(index, cols)
        x = margin + col * (cell_w + margin)
        y = top + row * (cell_h + margin)
        root.append(_rect(x, y, cell_w, cell_h, _CELL))
        root.append(
            label.Label(
                terminalio.FONT,
                text=text[:8],
                color=_TEXT,
                scale=2,
                anchor_point=(0.5, 0.5),
                anchored_position=(x + cell_w // 2, y + cell_h // 2),
            )
        )

    display.root_group = root
    display.refresh()  # static screen: draw once
    return display
