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

    def closest(rgb, block=None):
        r, g, b = rgb
        i = 0
        current_min = float('inf')
        current_ansi = None
        distance_table = []

        if block == 'standard':
            accepted_codes = range(8)
        elif block == 'intensive':
            accepted_codes = range(9, 9+8)
        elif block == 'cube':
            accepted_codes = range(16, 232)
        elif block == 'grayscale':
            accepted_codes = range(232, 256)
        elif block is not None:
            if type(eval(block)) == range or type(eval(block)) == list:
                accepted_codes = eval(block)
            else:
                accepted_codes = range(256)
        else:
            accepted_codes = range(256)

        for color in ANSI.colors:
            distance = sqrt(
                (r - color[0]) ** 2 + (g - color[1]) ** 2 + (b - color[2]) ** 2
            )

            if distance < current_min:
                if i in accepted_codes:
                    current_min = distance
                    current_ansi = i
            i += 1

        return current_ansi
