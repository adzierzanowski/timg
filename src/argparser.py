import argparse

from .version import TIMG_PROG_NAME, TIMG_DESC

def parse_args():
  parser = argparse.ArgumentParser(
    TIMG_PROG_NAME,
    description=TIMG_DESC)

  parser.add_argument(
    '-V', '--version',
    help='print version and exit',
    action='store_true')

  parser.add_argument(
    'filename',
    nargs='?',
    type=str,
    help='filename of an image')

  parser.add_argument(
    '-i', '--invert-background',
    help='invert grayscale in ASCII mode',
    action='store_true')

  parser.add_argument(
    '-m', '--method',
    type=str,
    help='''name of a rendering method (use `-m list` to list available methods,
    the default is a24h)''',
    metavar='METHOD',
    default='a24h')

  parser.add_argument(
    '-r', '--reduce-colors',
    type=int,
    help='reduce color palette of an input image (1-256)',
    metavar='N')

  parser.add_argument(
    '-s', '--size',
    type=int,
    help='width of an image',
    metavar='W')

  args = parser.parse_args()
  return parser, args