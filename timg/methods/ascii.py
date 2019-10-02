import math

from .method import RenderMethod


class ASCIIMethod(RenderMethod):
  CHARSETS = {
    'simple': ' .:-=+*#%@',
    'extended': ' .\'`^",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$'
  }

  def __init__(self, image, invert_background=False, charset='simple'):
    RenderMethod.__init__(self, image)
    self.invert_background = invert_background
    self.chars = ASCIIMethod.CHARSETS[charset]

  def grayscale(self):
    self.image = self.image.convert('L')

  def to_string(self):
    w, _ = self.image.size

    self.grayscale()
    pix = self.image.getdata()

    string = ''
    if self.invert_background:
      self.chars = list(reversed(self.chars))
    line_counter = 0
    div = math.ceil(255 / len(self.chars))
    for i, p in enumerate(pix):
      if line_counter % 2 == 0:
        string += self.chars[p // div - 1]
      if i % w == w-1:
        if line_counter % 2 == 0:
          string += '\n'
        line_counter += 1

    return string

def show_available_charsets():
  print('Available charsets:')
  for charset in ASCIIMethod.CHARSETS:
    print('  * {}'.format(charset))
