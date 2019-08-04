from .method import RenderMethod

class ASCIIMethod(RenderMethod):
  CHARS = ' .:-=+*#%@'

  def __init__(self, image, invert_background=False):
    RenderMethod.__init__(self, image)
    self.invert_background = invert_background

  def grayscale(self):
    self.image = self.image.convert('L')

  def to_string(self):
    w, _ = self.image.size

    self.grayscale()
    pix = self.image.getdata()

    string = ''
    chars = ASCIIMethod.CHARS
    if self.invert_background:
      chars = list(reversed(chars))
    line_counter = 0
    div = 255 // len(chars)
    for i, p in enumerate(pix):
      if line_counter % 2 == 0:
        string += chars[p // div - 1]
      if i % w == w-1:
        if line_counter % 2 == 0:
          string += '\n'
        line_counter += 1

    return string
