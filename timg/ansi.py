import sys
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

    def parse_block(block):
        ranges = block.split(',')
        codes = []
        for rng in ranges:
            rng_bounds = [int(n) for n in rng.split('..')]

            if len(rng_bounds) == 1:
                codes.append(rng_bounds[0])

            elif len(rng_bounds) == 2:
                codes += list(range(*rng_bounds))

            else:
                pass

        return codes

    # Return closest 8-bit ANSI color code for a given RGB value
    def closest(rgb, block=None):
        blocks = {
            'standard': range(8),
            'intensive': range(9, 17),
            'cube': range(16, 232),
            'grayscale': range(232, 256)
        }

        if block is None:
            accepted_codes = range(256)
        else:
            try:
                accepted_codes = blocks[block]
            except KeyError:
                try:
                    accepted_codes = ANSI.parse_block(block)
                except ValueError:
                    sys.stderr.write('Couldn\'t parse the block.\n')
                    sys.exit(1)

        i = 0
        r, g, b = rgb
        current_min = float('inf')
        current_ansi = None

        for color in ANSI.colors:
            cr, cg, cb = color
            rgb_difference = r - cr, g - cg, b - cb

            # this is simply a distance between two points in R^3 space
            distance = sqrt(sum(map(lambda m: pow(m, 2), rgb_difference)))

            if distance < current_min:
                if i in accepted_codes:
                    current_min = distance
                    current_ansi = i
            i += 1

        return current_ansi
