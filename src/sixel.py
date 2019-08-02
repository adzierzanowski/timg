#!/usr/bin/env python3

import time
import threading
from PIL import Image


class Sixel:
  def __init__(self):
    self.poschar = '?@ACGO_'
    self.header = '\033Pq'
    self.trailer = '\033\\'
    self.registers = {}
    self.register_count = 0
    self.palette_size = 0

    self.base_image = None
    self.image = None
    self.pix = None

    self.progress = 0.0
    self.progress_done = False

    self.print_thread = None
    self.load_file_thread = None
    self.progress_thread = None

  @staticmethod
  def pattern_to_char(n):
    return chr(n+63)

  def load_image_from_file(self, fname):
    # TODO: threading in this file is a total mess
    # and is probably unnecesarry
    self.progress_done = False
    self.progress_thread = threading.Thread(target=self.print_progress)
    self.load_file_thread = threading.Thread(target=self.load_file, args=(fname,))
    self.progress_thread.start()
    self.load_file_thread.start()
    self.load_file_thread.join()

  def load_file(self, fname):
    self.progress = 0.025

    self.base_image = Image.open(fname)
    self.progress += 0.025

    self.image = self.base_image.copy()
    self.progress += 0.0025

    self.reduce_colors(16)
    self.progress += 0.025

  def reduce_colors(self, n):
    self.palette_size = n
    image = self.image.convert(
      'P', palette=Image.ADAPTIVE, colors=self.palette_size)
    image = image.convert(
      'RGB', palette=Image.ADAPTIVE, colors=self.palette_size)
    self.image = image
    self.pix = self.image.load()

  def resize(self, w, h=None):
    if h is None:
      w_, h_ = self.image.size
      k = w / w_
      h = int(k * h_)

    image = self.image.resize((w, h))
    self.image = image
    self.pix = self.image.load()

  def print(self):
    self.progress = 0.0
    self.print_thread = threading.Thread(target=self.print_)
    self.print_thread.start()
    self.print_thread.join()

  def print_progress(self):
    while True:
      print('\r{:0.2f}%'.format(100*self.progress), end='')
      if self.progress_done:
        print('\r' + ' ' * 40)
        break
      time.sleep(0.01)

  def print_(self):
    self.progress_done = False
    self.progress = 0.1

    w, h = self.image.size

    # define color registers
    for i, (_, color) in enumerate(self.image.getcolors()):
      self.registers[color] = i
      self.register_count += 1

    color_data = {}
    color_count = len(self.registers)

    for color, reg_n in self.registers.items():
      color_data[reg_n] = []
      lines_total = h // 6

      for l in range(lines_total): # for every 6-pixel high line
        color_data[reg_n].append([])
        line_data = color_data[reg_n][-1]

        for x in range(w):
          self.progress += 0.8 * 1/(lines_total*color_count*w)
          line_chunk = 0
          for y in range(6):
            line_chunk |= int(self.pix[x, y+l*6] == color) << y
          line_data.append(line_chunk)

    lines = []

    for l in range(h//6):
      lines.append([])
      ldata = lines[-1]

      for reg, cdata in color_data.items():
        self.progress += 0.1 * 1/(h//6 * len(color_data))
        ending = '$' if reg < self.register_count - 1 else '-'
        ldata.append('#{}{}{}'.format(
          reg,
          ''.join([Sixel.pattern_to_char(p) for p in cdata[l]]),
          ending))

    lines = [''.join(ldata) for ldata in lines]

    self.progress_done = True
    self.progress_thread.join()

    print(self.header)
    for color, reg in self.registers.items():
      rgb = [int(100*c/255) for c in color[:3]]
      print('#{};2;{};{};{}'.format(reg, *rgb))
    print(lines)
    print(self.trailer)
