import random
import re

import pytest
from PIL import Image

from timg.methods.sixel import SixelMethod


TOKEN = re.compile(
    r"#(?P<reg>\d+)(?:;(?P<mode>\d+);(?P<p1>\d+);(?P<p2>\d+);(?P<p3>\d+))?"
    r"|!(?P<count>\d+)(?P<rep>[?-~])"
    r"|(?P<char>[?-~])"
    r"|(?P<cr>\$)"
    r"|(?P<lf>-)"
)


def decode(text, size):
    """Decode a sixel stream into (palette, per-pixel register grid)."""
    w, h = size
    assert text.startswith(SixelMethod.HEADER)
    assert text.endswith(SixelMethod.TRAILER)
    body = text[len(SixelMethod.HEADER) : -len(SixelMethod.TRAILER)]

    palette = {}
    grid = [[None] * w for _ in range(h)]
    reg = 0
    x = 0
    top = 0
    pos = 0
    while pos < len(body):
        match = TOKEN.match(body, pos)
        assert match is not None, f"bad token at {pos}: {body[pos:pos + 16]!r}"
        pos = match.end()

        if match.group("reg") is not None:
            reg = int(match.group("reg"))
            if match.group("mode") is not None:
                assert match.group("mode") == "2"
                palette[reg] = tuple(
                    int(match.group(g)) for g in ("p1", "p2", "p3")
                )
        elif match.group("cr"):
            x = 0
        elif match.group("lf"):
            x = 0
            top += 6
        else:
            if match.group("count") is not None:
                count = int(match.group("count"))
                char = match.group("rep")
            else:
                count = 1
                char = match.group("char")
            bits = ord(char) - 63
            for _ in range(count):
                assert x < w, "wrote past the right edge"
                for y in range(6):
                    if bits >> y & 1:
                        assert grid[top + y][x] is None, "pixel written twice"
                        grid[top + y][x] = reg
                x += 1

    return palette, grid


def image_from_pixels(size, pixels):
    image = Image.new("RGB", size)
    image.putdata(pixels)
    return image


def flat(size, color=(10, 20, 30)):
    w, h = size
    return image_from_pixels(size, [color] * (w * h))


def stripes(size):
    w, h = size
    palette = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    return image_from_pixels(size, [palette[y % 3] for y in range(h) for _ in range(w)])


def runs(size):
    """Long horizontal runs, to exercise the RLE path."""
    w, h = size
    palette = [(0, 0, 0), (255, 255, 255), (128, 64, 32)]
    return image_from_pixels(
        size, [palette[(x // 7 + y // 6) % 3] for y in range(h) for x in range(w)]
    )


def many_colors(size):
    """Every pixel a distinct color, to exceed the 256-register byte path."""
    w, h = size
    return image_from_pixels(
        size, [(i % 256, i // 256 % 256, i // 65536 % 256) for i in range(w * h)]
    )


def noise(size, colors, seed=0):
    w, h = size
    rng = random.Random(seed)
    palette = [
        (rng.randrange(256), rng.randrange(256), rng.randrange(256))
        for _ in range(colors)
    ]
    return image_from_pixels(size, [rng.choice(palette) for _ in range(w * h)])


@pytest.mark.parametrize(
    "image",
    [
        flat((10, 12)),
        flat((3, 6)),  # narrower than the RLE threshold
        stripes((16, 18)),
        stripes((16, 7)),  # height not a multiple of 6
        runs((40, 24)),
        noise((20, 12), 5),
        noise((20, 12), 200),
        many_colors((32, 12)),  # more colors than fit in a byte
    ],
    ids=[
        "flat",
        "narrow",
        "stripes",
        "ragged",
        "runs",
        "few-colors",
        "many-colors",
        "over-256-colors",
    ],
)
def test_decodes_back_to_original_pixels(image):
    w, h = image.size
    method = SixelMethod(image)
    palette, grid = decode(method.to_string(), image.size)

    # Only complete 6-row bands are emitted
    encoded_rows = (h // 6) * 6
    for y in range(encoded_rows):
        for x in range(w):
            reg = grid[y][x]
            assert reg is not None, f"pixel ({x}, {y}) never written"
            assert reg == method.registers[image.getpixel((x, y))]
            assert palette[reg] == tuple(
                SixelMethod.rgb_to_percent(image.getpixel((x, y)))
            )

    # Nothing beyond the last full band
    for y in range(encoded_rows, h):
        assert grid[y] == [None] * w


def expand(text):
    """Inverse of SixelMethod._rle."""
    out = []
    pos = 0
    while pos < len(text):
        if text[pos] == "!":
            match = re.compile(r"!(\d+)(.)").match(text, pos)
            out.append(match.group(2) * int(match.group(1)))
            pos = match.end()
        else:
            out.append(text[pos])
            pos += 1
    return "".join(out)


@pytest.mark.parametrize(
    "chars",
    [
        "",
        "?",
        "???",
        "????",
        "?????",
        "??@@@@AB",
        "~" * 300,
        "?@" * 50,
        "AAAABBBBAAAA",
    ],
)
def test_rle_round_trips(chars):
    assert expand(SixelMethod._rle(chars)) == chars


def test_rle_compresses_long_runs():
    assert SixelMethod._rle("?" * 100) == "!100?"
    assert SixelMethod._rle("???") == "???"


def test_repeated_bands_reuse_cached_output():
    image = stripes((16, 36))  # 3-row period, so every 6-row band is identical
    text = SixelMethod(image).to_string()
    body = text[len(SixelMethod.HEADER) : -len(SixelMethod.TRAILER)]
    # The color register declarations precede the first band
    body = re.sub(r"^(?:#\d+;2;\d+;\d+;\d+)+", "", body)
    bands = [b for b in body.split("-") if b]
    assert len(bands) == 6
    assert len(set(bands)) == 1


def test_palette_mode_image_is_encoded_directly():
    rgb = runs((24, 12))
    image = rgb.convert("P", palette=Image.ADAPTIVE, colors=256)
    method = SixelMethod(image)
    palette, grid = decode(method.to_string(), image.size)

    reference = image.convert("RGB")
    for y in range(12):
        for x in range(24):
            reg = grid[y][x]
            assert reg is not None
            assert palette[reg] == tuple(
                SixelMethod.rgb_to_percent(reference.getpixel((x, y)))
            )


def test_duplicate_palette_entries_share_one_register():
    image = Image.new("P", (8, 6))
    # Two palette slots, same color; only slot 1 is used by the pixels.
    image.putpalette([9, 9, 9, 9, 9, 9] + [0] * 762)
    image.putdata([1] * 48)

    method = SixelMethod(image)
    text = method.to_string()

    assert method.register_count == 1
    assert list(method.registers) == [(9, 9, 9)]
    palette, grid = decode(text, image.size)
    assert {reg for row in grid for reg in row} == {0}
    assert palette == {0: (3, 3, 3)}


def test_high_color_image_falls_back():
    image = many_colors((32, 12))
    method = SixelMethod(image)
    assert method._indexed_data() is None
    # Still encodes correctly through the generic path
    decode(method.to_string(), image.size)


def test_lossless_palette_path_is_used_for_low_color_images():
    image = runs((40, 24))
    method = SixelMethod(image)
    assert method._indexed_data() is not None
