from .method import RenderMethod

class SixelMethod(RenderMethod):
  # Sixel stream beginning
  # There is some optional config between P and q but we don't use it
  HEADER = '\033Pq'

  # Sixel stream ending
  TRAILER = '\033\\'

  @staticmethod
  def pattern_to_char(n):
    '''Returns a character corresponding to a 6-pixel pattern'''
    return chr(n+63)

  @staticmethod
  def rgb_to_percent(rgb):
    '''As sixel RGB format requires values from 0 to 100,
    this method converts standard 8-bit collections to such
    crazy thing'''
    return [int(100*c/255) for c in rgb]

  def __init__(self, image):
    RenderMethod.__init__(self, image)

    # Color registers
    # The maximum value varies from terminal to terminal
    self.registers = {}
    self.register_count = 0

  def to_string(self):
    w, h = self.image.size
    pix = self.image.load()

    # Total number of 6-pixel high lines
    line_count = h // 6

    # Define color registers
    register_string = ''
    for i, (_, color) in enumerate(self.image.getcolors(maxcolors=0x1000000)):
      self.registers[color] = i
      self.register_count += 1
      register_string += '#{};2;{};{};{}'.format(
        i, *SixelMethod.rgb_to_percent(color[:3]))

    line_data = []
    for l in range(line_count):
      line_string = ''
      for color, reg in self.registers.items():
        color_string = '#{}'.format(reg)
        for x in range(w):
          chunk = 0
          for y in range(6):
            chunk |= int(pix[x, y+l*6] == color) << y
          color_string += SixelMethod.pattern_to_char(chunk)
        line_string += color_string
        if reg < self.register_count - 1:
          line_string += '$'
        else:
          line_string += '-'
      line_data.append(line_string)

    return '{}{}{}{}'.format(
      SixelMethod.HEADER,
      register_string,
      ''.join(line_data),
      SixelMethod.TRAILER)
