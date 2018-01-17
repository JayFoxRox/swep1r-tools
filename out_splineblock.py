#!/usr/bin/env python3

import struct

import os
from PIL import Image

from arguments import parser


def read8(f):
  return f.read(1)[0]
def read16(f):
  return int.from_bytes(f.read(2), byteorder='big', signed=False)
def read32(f):
  return int.from_bytes(f.read(4), byteorder='big', signed=False)
def readFloat(f):
  return struct.unpack('>f', f.read(4))[0]

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
    f.seek(4 + 4 * i)
    a = read32(f)
    b = read32(f)
    length = b - a

    print("%d: a: 0x%08X b: 0x%08X (length: %d)" % (i, a, b, length))

    f.seek(a)
    buf = f.read(length)

    spline_bin = os.path.join(args.out, 'spline-%d.bin' % i)
    with open(spline_bin, 'wb') as t:
      t.write(buf)

    spline_obj = os.path.join(args.out, 'spline-%d.obj' % i)
    t = open(spline_obj, 'w')

    f.seek(a)

    read32(f) # [0]
    count = read32(f) # array count [4]
    read32(f) # [8]

    read32(f) # wtf?! skipping 4 byte?
  
    # some array [16]

    print("Next spline! (%d)" % count)
    for i in range(0, count):
      before = f.tell()
      print("unk0: 0x%04X" % read16(f)) # Read 1 x short [0]
      print("unk1: 0x%04X" % read16(f)) # Read 1 x short [2]
      print("unk2[0]: 0x%04X (next index?)" % read16(f)) # Read 2 x short [4]
      print("unk2[1]: 0x%04X" % read16(f)) 
      print("unk3[0]: 0x%04X (prev index?)" % read16(f)) # Read 4 x short [8]
      print("unk3[1]: 0x%04X" % read16(f)) 
      print("unk3[2]: 0x%04X" % read16(f)) 
      print("unk3[3]: 0x%04X" % read16(f)) 
      pos = (readFloat(f), readFloat(f), readFloat(f))
      normal = (readFloat(f), readFloat(f), readFloat(f))
      print("pos?: %f %f %f" % pos) # Read 3 x dword [16]
      print("normal?: %f %f %f" % normal) # Read 3 x dword [28]
      print("unka: %f %f %f" % (readFloat(f), readFloat(f), readFloat(f))) # Read 3 x dword [40]
      print("unkb: %f %f %f" % (readFloat(f), readFloat(f), readFloat(f))) # Read 3 x dword [52]
      print("unk8: 0x%04X (index?)" % read16(f)) # Read 1 x short [64]
      print("unk9[0]: 0x%04X (index?)" % read16(f)) # Read 8 x short [66]
      print("unk9[1]: 0x%04X" % read16(f))
      print("unk9[2]: 0x%04X" % read16(f))
      print("unk9[3]: 0x%04X" % read16(f))
      print("unk9[4]: 0x%04X" % read16(f))
      print("unk9[5]: 0x%04X" % read16(f))
      print("unk9[6]: 0x%04X" % read16(f))
      print("unk9[7]: 0x%04X" % read16(f))
      print("unk10: 0x%04X" % read16(f))
      after = f.tell()
      assert((after - before) == 84)
      # ???
      # = 84

      t.write("vn %f %f %f\n" % normal)
      t.write("v %f %f %f\n" % pos)

    t.close()

    assert(f.tell() - a == b - a)
