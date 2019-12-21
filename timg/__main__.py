import shutil
import sys

import timg

from .methods import METHODS, show_available_methods
from .methods.ascii import show_available_charsets


def main():
  parser, args = timg.argparser.parse_args()

  if args.version:
    print(timg.meta.NAME, timg.meta.VERSION)
    sys.exit(1)

  if args.method == 'list':
    show_available_methods()
    sys.exit(0)

  if args.charset == 'list':
    show_available_charsets()
    sys.exit(0)

  if args.filename is None:
    parser.print_usage()
    print('No filename specified.')
    sys.exit(1)

  renderer = timg.Renderer()
  renderer.load_image_from_file(args.filename)

  if args.size is not None:
    renderer.resize(args.size)

  if args.reduce_colors is not None:
    renderer.reduce_colors(args.reduce_colors)

  try:
    method = METHODS[args.method]['class']
  except KeyError:
    print('No such method.')
    show_available_methods()
    sys.exit(1)

  if method == timg.SixelMethod:
    if args.reduce_colors is None:
      renderer.reduce_colors(16)

  elif method in [
    timg.Ansi24FblockMethod,
    timg.Ansi24HblockMethod,
    timg.Ansi8FblockMethod,
    timg.Ansi8HblockMethod,
    timg.ASCIIMethod]:
    if args.size is None:
      renderer.resize(shutil.get_terminal_size()[0] - 1)

  if method == timg.ASCIIMethod:
    renderer.render(method, args.invert_background, args.charset)
  else:
    renderer.render(method)

if __name__ == '__main__':
  main()
