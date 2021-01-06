import argparse

from platform import system

from . import meta


def parse_args():
  parser = argparse.ArgumentParser(
    meta.NAME,
    description=meta.DESC)

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
    '-c', '--charset',
    type=str,
    help='''character set to be used in ASCII mode (type `-c list` to list
    available charsets, the default is simple)''',
    default='simple'
  )

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
    default='a24h' if system() != "Windows" else "ascii")

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
