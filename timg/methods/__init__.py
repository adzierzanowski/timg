from .ansi_methods import (
  Ansi8FblockMethod,
  Ansi8HblockMethod,
  Ansi24FblockMethod,
  Ansi24HblockMethod
)
from .ascii import ASCIIMethod
from .sixel import SixelMethod

METHODS = {
'sixel': {
  'class': SixelMethod,
  'desc': 'use sixels - best quality but lowest support'
},

'a8f': {
  'class': Ansi8FblockMethod,
  'desc': 'low-resolution ANSI 8-bit palette'
},

'a24f': {
  'class': Ansi24FblockMethod,
  'desc': 'low-resolution ANSI 24-bit palette',
},

'a8h': {
  'class': Ansi8HblockMethod,
  'desc': 'high-resolution ANSI 8-bit palette'
},

'a24h': {
  'class': Ansi24HblockMethod,
  'desc': 'high-resolution ANSI 24-bit palette'
},

'ascii': {
  'class': ASCIIMethod,
  'desc': 'ASCII art'
}
}

def show_available_methods():
  print('Available methods:')
  for k, v in METHODS.items():
    print('  * {:10} {}'.format(k, v['desc']))
