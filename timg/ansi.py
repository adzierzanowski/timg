import json

from pkg_resources import resource_filename
from math import sqrt


class ANSI:
    colors_filename = resource_filename(__name__, 'ansi_color_codes.json')
    with open(colors_filename, 'r') as f:
        colors = json.loads(f.read())

    end = "\033[0m"

    def fg(color_code):
        return "\033[38;5;{}m".format(color_code)

    def bg(color_code):
        return "\033[48;5;{}m".format(color_code)

    def fg_true(r, g, b):
        return "\033[38;2;{};{};{}m".format(r, g, b)

    def bg_true(r, g, b):
        return "\033[48;2;{};{};{}m".format(r, g, b)

    # Return closest 8-bit ANSI color code for a given RGB value
    def closest(rgb, block=None):
        if block == 'standard':
            accepted_codes = range(8)
        elif block == 'intensive':
            accepted_codes = range(9, 9+8)
        elif block == 'cube':
            accepted_codes = range(16, 232)
        elif block == 'grayscale':
            accepted_codes = range(232, 256)
        elif block is not None:
            block_type = type(eval(block))
            if block_type in [range, list]:
                accepted_codes = eval(block)
            else:
                accepted_codes = range(256)
        else:
            accepted_codes = range(256)

        i = 0
        r, g, b = rgb
        current_min = float('inf')
        current_ansi = None

        for color in ANSI.colors:
            cr, cg, cb = color
            rgb_difference = r - cr, g - cg, b - cb
            distance = sqrt(sum(map(lambda m: pow(m, 2), rgb_difference)))

            if distance < current_min:
                if i in accepted_codes:
                    current_min = distance
                    current_ansi = i
            i += 1

        return current_ansi
