import sys
from PIL import Image
from random import choice

from .ansi import ANSI


# Create bloxels (terminal character "pixels") from a PIL Image
def create_bloxels(image, size=70, high_resolution=False):
    w, h = image.size

    # width and height of an image mapped onto a bloxel
    bw = w // size
    if high_resolution:
        bh = h // int(size * h/w)
    else:
        bh = h // int((size / 1.9) * h/w)

    # bloxels count in both dimensions
    bloxels_w = w // bw
    bloxels_h = h // bh

    image = image.resize((bloxels_w, bloxels_h))
    pixels = image.load()

    bloxels = []

    # populate bloxels map with RGB tuples
    for hc in range(bloxels_h):
        bloxels.append([])
        for wc in range(bloxels_w):
            try:
                bloxels[hc].append(pixels[wc, hc][:3])
            except IndexError:
                pass

    return bloxels


# Display bloxels
def display(bloxels,
            high_resolution=False,
            charset=None,
            true_color=False,
            random_chars=False,
            block=None):
    if high_resolution:
        even = bloxels[0::2]
        odd = bloxels[1::2]

        for i, row in enumerate(even):
            for j, col in enumerate(row):
                try:
                    print(
                            "{}{}▄".format(
                                ANSI.bg_true(*col),
                                ANSI.fg_true(*odd[i][j])
                                ), end=''
                            )
                except IndexError:
                    pass
            print(ANSI.end)

    else:
        i = 0
        for row in bloxels:
            for col in row:
                if true_color:
                    if charset is None:
                        print("{} ".format(ANSI.bg_true(*col)), end='')
                    else:
                        if random_chars:
                            char = choice(charset)
                        else:
                            char = charset[i % len(charset)]
                        print("{}{}".format(ANSI.fg_true(*col), char), end='')
                else:
                    color_code = ANSI.closest(*col, block)
                    if charset is None:
                        print("{} ".format(ANSI.bg(color_code)), end='')
                    else:
                        if random_chars:
                            char = choice(charset)
                        else:
                            char = charset[i % len(charset)]
                        print("{}{}".format(ANSI.fg(color_code), char), end='')
                i += 1
            print(ANSI.end)
