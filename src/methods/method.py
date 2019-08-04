class RenderMethod:
  def __init__(self, image):
    self.image = image

  def to_string(self):
    raise NotImplementedError('Renderer::to_string() should be implemented!')
