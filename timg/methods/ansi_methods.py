from .ansi import ANSIMethod
from .method import RenderMethod


class Ansi8FblockMethod(RenderMethod):
  def __init__(self, image):
    super().__init__(image)

  def to_string(self):
    return ANSIMethod(self.image).to_8_bit_fblock()

class Ansi24FblockMethod(RenderMethod):
  def __init__(self, image):
    super().__init__(image)

  def to_string(self):
    return ANSIMethod(self.image).to_24_bit_fblock()

class Ansi8HblockMethod(RenderMethod):
  def __init__(self, image):
    super().__init__(image)

  def to_string(self):
    return ANSIMethod(self.image).to_8_bit_hblock()

class Ansi24HblockMethod(RenderMethod):
  def __init__(self, image):
    super().__init__(image)

  def to_string(self):
    return ANSIMethod(self.image).to_24_bit_hblock()
