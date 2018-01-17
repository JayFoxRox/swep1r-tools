#!/usr/bin/env python3

import os
from PIL import Image

from arguments import parser


def read8(f):
  return f.read(1)[0]
def read16(f):
  return int.from_bytes(f.read(2), byteorder='big', signed=False)
def read32(f):
  return int.from_bytes(f.read(4), byteorder='big', signed=False)

def shifter(a1):
  v1 = 0x40000000
  v2 = 31
  while(v2 != 0):
    v3 = a1 & v1
    v1 >>= 1
    --v2
    if v3 == 0:
      break
  result = 2 * v1
  if ( result < a1 ):
    result *= 2
  if ( result < 16 ):
    result = 16
  return result


args = parser.parse_args()


with open(args.input, 'rb') as f:
  count = read32(f)
  for i in range(0, count - 1):
    f.seek(4 + 8 * i)
    a = read32(f)
    b = read32(f)
    c = read32(f)
    length = c - a

    if b != 0:
      continue

    print("%d: a: 0x%08X b: 0x%08X (c: 0x%08X; length: %d or %d bytes)" % (i, a, b, c, b - a, length))

    f.seek(a)
    buf = f.read(length)

    texture = os.path.join(args.out, "texture-%d.bin" % i)
    with open(texture, 'wb') as t:
      f.read
      t.write(buf)

    f.seek(a)
    mode = read8(f)
    print("  - mode: %d" % mode)

    if False:

      if length != 2080:
        continue

      if mode != 1:
        continue

    #im = PIL.Image.frombytes('RGBA', (32, 32), buf[1:], decoder_name='raw')

    if b == 0:
      if length == 128:
        width = 32 // 8
        height = 32 // 4
      elif length == 256:
        width = 32 // 4
        height = 32 // 4
      elif length == 512:
        width = 32 // 4
        height = 32 // 2
      elif length == 1024:
        width = 32 // 2
        height = 32 // 2
      elif length == 2048:
        width = 32
        height = 32 // 2
      elif length == 2800:
        #FIXME!!!
        width = 1
        height = 1
      elif length == 4096:
        # Some of these are 64*16, others seem to be 32x32
        width = 32 * 2
        height = 32 // 2
        #width = 32
        #height = 32
      else:
        assert(False)

      im = Image.new("RGBA", (width, height))
      pixels = im.load()
      for y in range(0, height):
        for x in range(0, width):
          #pixel = int.from_bytes(f.read(2), byteorder='big', signed=False) #read16(f)
          r, g, b, a = f.read(4)
          #r = ((pixel >> 0) & 0x1F) * 0xFF // 0x1F
          #g = 0 #((pixel >> 5) & 0x1F) * 0xFF // 0x1F
          #b = 0 #((pixel >> 10) & 0x1F) * 0xFF // 0x1F
          pixels[x, y] = (a, r, g, b)
      texture = os.path.join(args.out, 'texture-%d.png' % i)
      im.save(texture, 'PNG')


    if False:
      if (a2 == 1257):
        dword_50C620 = (int)*a3;
      if ( a2 == 1258 ):
        dword_50C624 = (int)*a3;
      if ( a2 == 936 ):
        dword_50C618 = (int)*a3;
      if ( a2 == 352 ):
        dword_50C61C = (int)*a3;
      if ( a2 == 118 ):
        pass # run "invcol" filter
