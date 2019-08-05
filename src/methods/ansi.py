class ANSIMethod:
  TRAILER = '\033[0m'

  @staticmethod
  def rgb8(r, g, b):
    '''Return 8-bit color code from an rgb value'''

    # If grayscale
    if all([
      abs(r-g) < 10,
      abs(r-b) < 10,
      abs(g-b) < 10]):

      avg = (r+g+b)/3
      grayscale_step = int(avg/10.625) - 1
      code = 232 + grayscale_step

    else:
      r_, g_, b_ = [int(c/51) for c in (r, g, b)]
      code = 16 + 36*r_ + 6*g_ + b_

    return code

  @staticmethod
  def fg8(r, g, b):
    '''Return 8-bit fg color ANSI escape sequence from an rgb value'''
    return '\033[38;5;{}m'.format(ANSIMethod.rgb8(r, g, b))

  @staticmethod
  def bg8(r, g, b):
    '''Return 8-bit bg color ANSI escape sequence from an rgb value'''
    return "\033[48;5;{}m".format(ANSIMethod.rgb8(r, g, b))

  @staticmethod
  def fg24(r, g, b):
    '''Return 24-bit fg color ANSI escape sequence from an rgb value'''
    return "\033[38;2;{};{};{}m".format(r, g, b)

  @staticmethod
  def bg24(r, g, b):
    '''Return 24-bit bg color ANSI escape sequence from an rgb value'''
    return "\033[48;2;{};{};{}m".format(r, g, b)

  def __init__(self, image):
    self.image = image

  def to_block(self, bits, hblock=False):
    w, h = self.image.size
    pix = self.image.load()

    string = ''

    for y in range(0, h, 2):
      for x in range(w):
        try:
          fg_color = pix[x, y+1][:3]
          bg_color = pix[x, y][:3]
        except IndexError:
          continue

        if bits == 8:
          fg, bg = (
            ANSIMethod.fg8(*fg_color),
            ANSIMethod.bg8(*bg_color))

        elif bits == 24:
          fg, bg = (
            ANSIMethod.fg24(*fg_color),
            ANSIMethod.bg24(*bg_color))

        if hblock:
          string += '{}{}▄'.format(fg, bg)
        else:
          string += '{} '.format(bg)
      string += '{}\n'.format(ANSIMethod.TRAILER)

    return string

  def to_8_bit_hblock(self):
    return self.to_block(8, hblock=True)

  def to_24_bit_hblock(self):
    return self.to_block(24, hblock=True)

  def to_8_bit_fblock(self):
    return self.to_block(8, hblock=False)

  def to_24_bit_fblock(self):
    return self.to_block(24, hblock=False)
