from .method import RenderMethod

class ASCIIMethod(RenderMethod):
  CHARS = ' .:-=+*#%@'

  def __init__(self, image):
    RenderMethod.__init__(self, image)

  def grayscale(self):
    self.image = self.image.convert('L')

  def to_string(self):
    w, _ = self.image.size

    self.grayscale()
    pix = self.image.getdata()

    string = ''
    line_counter = 0
    div = 255 // len(ASCIIMethod.CHARS)
    for i, p in enumerate(pix):
      if line_counter % 2 == 0:
        string += ASCIIMethod.CHARS[p//div]
      if i % w == w-1:
        if line_counter % 2 == 0:
          string += '\n'
        line_counter += 1

    return string
