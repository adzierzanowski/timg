from PIL import Image


class Renderer:
  def __init__(self):
    self.image = None

  def load_image_from_file(self, fname):
    self.load_image(Image.open(fname))

  def load_image(self, image):
    self.image = image

  def resize(self, w, h=None):
    current_w, current_h = self.image.size

    if h is None:
      ratio = w / current_w
      h = int(ratio * current_h)

    self.image = self.image.resize((w, h))

  def reduce_colors(self, n):
    self.image = self.image.convert('P', palette=Image.ADAPTIVE, colors=n)
    self.image = self.image.convert('RGB', palette=Image.ADAPTIVE, colors=n)

  def grayscale(self):
    self.image = self.image.convert('L')

  def to_string(self, method_class, *args, **kwargs):
    method = method_class(self.image, *args, **kwargs)
    return method.to_string()

  def render(self, method_class, *args, **kwargs):
    print(self.to_string(method_class, *args, **kwargs))
