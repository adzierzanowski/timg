"""Sixel encoder.

A sixel stream draws an image in horizontal bands six pixels tall. Within a
band, each printable character carries one column of six pixels as a bitmask
(bit 0 = top row), biased by 63 so the byte stays in the printable ASCII range
'?'..'~'. Only one color can be drawn at a time, so a band is emitted once per
color present in it:

    #<reg>;2;<r>;<g>;<b>   declare color register <reg> as RGB percentages
    #<reg>                 select color register <reg>
    !<count><char>         repeat <char> <count> times (run-length encoding)
    $                      carriage return: back to column 0, same band
    -                      line feed: advance to the next band

So a band's output looks like "#0<data>$#1<data>$#2<data>-", where each color's
data covers the full band width and pixels of other colors are simply left
unset (bit clear) in that pass.

Everything here is arranged so the per-pixel work happens inside CPython's C
implementations (bytes.translate, int.from_bytes, re.sub) rather than in Python
loops, and so that repeated bands and repeated sub-bands are only encoded once.
"""

import re

from PIL import Image

from .method import RenderMethod


class SixelMethod(RenderMethod):
    # Sixel stream beginning
    # There is some optional config between P and q but we don't use it
    HEADER = "\033Pq"

    # Sixel stream ending
    TRAILER = "\033\\"

    # Translation table mapping a 6-pixel pattern (0..63) to its sixel byte.
    # Values above 63 never occur, so they are mapped to 0.
    _CHAR_TABLE = bytes(range(63, 127)) + bytes(192)

    # Matches any run of 4 or more identical sixel characters. Below 4 the
    # "!<count><char>" form is never shorter than the literal repetition
    # ("!4?" is 3 bytes vs "????", but "!3?" ties "???").
    _RUN = re.compile(r"(.)\1{3,}")

    # Modes whose pixels map directly onto RGB palette entries, i.e. where a
    # lossless conversion to at most 256 registers may exist. Anything else
    # (RGBA, CMYK, F, ...) goes down the generic path.
    _PALETTE_MODES = ("P", "RGB")

    @staticmethod
    def pattern_to_char(n):
        """Returns a character corresponding to a 6-pixel pattern"""
        return chr(n + 63)

    @staticmethod
    def rgb_to_percent(rgb):
        """As sixel RGB format requires values from 0 to 100,
        this method converts standard 8-bit collections to such
        crazy thing
        """
        return [int(100 * c / 255) for c in rgb]

    @staticmethod
    def _pixels(image):
        """Return a flat sequence of per-pixel values, matching the keys
        returned by getcolors().

        get_flattened_data() is identical to getdata(), which is deprecated
        in Pillow 12, so prefer it where it exists.
        """
        flatten = getattr(image, "get_flattened_data", None)
        return flatten() if flatten is not None else image.getdata()

    def __init__(self, image):
        RenderMethod.__init__(self, image)

        # Maps each distinct color to its register number. Populated by
        # to_string(); the tests rely on it to check what was emitted.
        # How many registers a terminal actually supports varies, so we just
        # use as many as the image needs.
        self.registers = {}
        self.register_count = 0

        # Memoization, shared across every band of one image:
        # _tables[reg]      -> the six bit-extraction tables for that register
        # _body_cache[data] -> the sixel string for one color's column patterns
        self._tables = {}
        self._body_cache = {}

    @staticmethod
    def _rle(chars):
        """Run-length encode a string of sixel characters into a compact string.
        Uses the sixel "!count char" syntax when a run of 4 or more repeats.
        The scan happens in C; Python is only called back on compressible runs.
        """
        return SixelMethod._RUN.sub(
            lambda m: "!{}{}".format(len(m.group(0)), m.group(1)), chars
        )

    def _bit_tables(self, reg):
        """Six 256-entry translation tables for `reg`: table `y` maps that
        register index to bit `1 << y` and every other index to 0.

        Applying table `y` to a row of register indices with bytes.translate
        therefore yields, in C, that row's contribution to the sixel patterns
        for this one color.
        """
        tables = self._tables.get(reg)
        if tables is None:
            tables = self._tables[reg] = [
                bytes((1 << y) if i == reg else 0 for i in range(256)) for y in range(6)
            ]
        return tables

    def _chunks_to_string(self, chunks, w):
        """Render one color's per-column sixel patterns (a bytes of values
        0..63) into a sixel data string, caching the result.

        The cache is keyed on the patterns themselves, so identical sub-bands
        of different colors, or of the same color in different bands, are only
        translated and run-length encoded once.
        """
        if not chunks:
            return ""

        cache = self._body_cache
        body = cache.get(chunks)
        if body is None:
            first = chunks[0]
            if chunks.count(first) == w:
                # Uniform band for this color: skip translate/RLE entirely.
                c = chr(first + 63)
                body = f"!{w}{c}" if w >= 4 else c * w
            else:
                body = SixelMethod._rle(
                    chunks.translate(SixelMethod._CHAR_TABLE).decode("latin-1")
                )
            cache[chunks] = body
        return body

    def _indexed_band_to_string(self, band, w):
        """Encode a 6-row band of register indices, given as a bytes object.

        The fast path: one byte per pixel means the whole band can be sliced
        into rows and processed with bytes.translate and integer arithmetic,
        without ever materializing per-pixel Python objects.
        """
        rows = [band[y * w : (y + 1) * w] for y in range(6)]

        # sorted() keeps the output deterministic, which the tests depend on.
        parts = []
        for reg in sorted(set(band)):
            tables = self._bit_tables(reg)
            # Treat each translated row as one huge big-endian integer and OR
            # the six of them together, combining all w columns in a single
            # operation. Every byte lane holds a value <= 63, so bits from
            # different rows can never carry out of their own column.
            acc = 0
            for y, row in enumerate(rows):
                acc |= int.from_bytes(row.translate(tables[y]), "big")
            chunks = acc.to_bytes(w, "big")
            parts.append(f"#{reg}{self._chunks_to_string(chunks, w)}")

        # Separate color sub-bands with '$' (carriage return), end band with '-'.
        return "$".join(parts) + "-"

    def _generic_band_to_string(self, band, w):
        """Encode a 6-row band of raw pixels, for images with more colors than
        fit in a byte.

        The slow path: pixels are arbitrary Python values (usually (r, g, b)
        tuples), so the band has to be walked column by column. Rare in
        practice, since terminals cannot show thousands of registers anyway.
        """
        rows = [band[y * w : (y + 1) * w] for y in range(6)]

        # For each color present in this band, accumulate its sixel pattern.
        # Insertion order decides the sub-band order here; unlike the indexed
        # path there is no cheap sort key, and correctness does not need one.
        band_patterns = {}
        get_patterns = band_patterns.get
        for x, column in enumerate(zip(*rows)):
            # Row y of the column contributes bit 1 << y to that color.
            bit = 1
            for color in column:
                patterns = get_patterns(color)
                if patterns is None:
                    # Initialize a per-column chunk buffer for this color, lazily.
                    patterns = bytearray(w)
                    band_patterns[color] = patterns
                patterns[x] |= bit
                bit <<= 1

        registers = self.registers
        parts = [
            f"#{registers[color]}{self._chunks_to_string(bytes(chunks), w)}"
            for color, chunks in band_patterns.items()
        ]
        return "$".join(parts) + "-"

    def _indexed_data(self):
        """Turn the image into one byte of register index per pixel using
        PIL's C-level palette machinery, populating self.registers.

        Returns (data, colors), or None if the image can't be represented
        losslessly by 256 or fewer registers.
        """
        image = self.image
        if image.mode not in SixelMethod._PALETTE_MODES:
            # Could be converted, but the caller's generic path handles these
            # correctly and they are uncommon; keep this function honest.
            return None

        if image.mode != "P":
            # getcolors() returns None past maxcolors, i.e. exactly when no
            # lossless palette exists.
            if image.getcolors(maxcolors=256) is None:
                return None
            reference = image.tobytes()
            image = image.convert("P", palette=Image.ADAPTIVE, colors=256)
            # Median cut is exact for <= 256 colors, but verify instead of
            # trusting it: one C-level comparison is cheap insurance.
            if image.convert("RGB").tobytes() != reference:
                return None

        palette = image.getpalette()
        if palette is None:
            return None
        if len(palette) < 768:
            # Pillow may return a short palette; pad so any index 0..255 can
            # be looked up without a bounds check below.
            palette = palette + [0] * (768 - len(palette))

        # For "P" mode this is the raw index plane, no copy of the pixels as
        # Python objects anywhere.
        data = image.tobytes()

        # Collapse duplicate palette entries and drop unused ones, so every
        # color gets exactly one register. Sorting by palette index keeps
        # register numbering stable for a given image.
        registers = self.registers
        colors = []
        table = bytearray(256)
        for index in sorted(set(data)):
            color = tuple(palette[index * 3 : index * 3 + 3])
            reg = registers.get(color)
            if reg is None:
                reg = registers[color] = len(colors)
                colors.append(color)
            table[index] = reg

        # Rewrite palette indices into register numbers in one C-level pass.
        return data.translate(bytes(table)), colors

    def to_string(self):
        w, h = self.image.size

        # Total number of 6-pixel high lines. A trailing partial band is
        # dropped: callers resize to a multiple of 6 when it matters.
        line_count = h // 6

        # Prefer PIL's palette conversion: it maps pixels to small integer
        # indices in C, so nothing walks the pixels in Python at all.
        indexed = self._indexed_data()
        if indexed is not None:
            data, colors = indexed
            band_to_string = self._indexed_band_to_string
        else:
            # No lossless byte-per-pixel representation, so build the register
            # map straight from the image's colors. maxcolors is set high
            # enough that getcolors() will not give up and return None.
            registers = self.registers
            colors = []
            for _, color in self.image.getcolors(maxcolors=0x1000000):
                registers[color] = len(colors)
                colors.append(color)

            # Bytes slice, hash and compare far faster than lists of (r, g, b)
            # tuples, but only hold 256 distinct values, so fall back past that.
            pixels = SixelMethod._pixels(self.image)
            if len(colors) <= 256:
                data = bytes(map(registers.__getitem__, pixels))
                band_to_string = self._indexed_band_to_string
            else:
                data = tuple(pixels)
                band_to_string = self._generic_band_to_string

        self.register_count = len(colors)

        # Declare every register up front, before any band data. color[:3]
        # discards any alpha or extra bands that survived to this point.
        rgb_to_percent = SixelMethod.rgb_to_percent
        register_string = "".join(
            "#{};2;{};{};{}".format(i, *rgb_to_percent(color[:3]))
            for i, color in enumerate(colors)
        )

        band_size = 6 * w
        # Keyed on the raw band data, so identical bands anywhere in the image
        # cost one dict lookup. Local to this call, since band_to_string
        # depends on which path we took above.
        band_cache = {}
        line_data = []
        for line in range(line_count):
            offset = line * band_size
            band = data[offset : offset + band_size]

            # Whole bands repeat constantly: flat backgrounds, borders,
            # letterboxing, upscaled images.
            line_string = band_cache.get(band)
            if line_string is None:
                line_string = band_cache[band] = band_to_string(band, w)
            line_data.append(line_string)

        return "{}{}{}{}".format(
            SixelMethod.HEADER, register_string, "".join(line_data), SixelMethod.TRAILER
        )
