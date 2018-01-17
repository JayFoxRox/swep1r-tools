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




if False:

  #//----- (0042D520) --------------------------------------------------------
  #_BYTE *__cdecl sub_42D520(char *a1, _BYTE *a2)
  #{
  #  char *v2; // edx
  #  _BYTE *result; // eax
  #  int v4; // ebp
  #  int v5; // esi
  #  char v6; // cl
  #  char v7; // bl
  #  char v8; // cl
  #  int v9; // ebx
  #  int v10; // ecx
  #  int v11; // ecx
  #  int v12; // ebx
  #  int v13; // ebx
  #  int v14; // edi
  #  int v15; // esi
  #  char v16; // dl
  #  bool v17; // sf
  #  unsigned __int8 v18; // of
  #  signed __int16 v19; // [esp+10h] [ebp-Ch]
  #  int v20; // [esp+14h] [ebp-8h]
  #  __int16 v21; // [esp+18h] [ebp-4h]
  #  char *v22; // [esp+20h] [ebp+4h]
  #  int v23; // [esp+24h] [ebp+8h]
  #
  #  v2 = a1;
  #  result = a2;
  #  v4 = (int)(a1 - 4096);
  #  v5 = 1;
  #  v19 = 0;
  #  do
  #  {
  #    v6 = *v2++;
  #    v7 = 0;
  #    v20 = v6;
  #    v23 = 0;
  #    while ( (1 << v7) & v20 )
  #    {
  #      v8 = *v2++;
  #      *result++ = v8;
  #      *(_BYTE *)(v5 + v4) = v8;
  #      v5 = ((_WORD)v5 + 1) & 0xFFF;
  #LABEL_11:
  #      v7 = v23 + 1;
  #      v18 = __OFSUB__(v23 + 1, 8);
  #      v17 = (signed __int16)(v23++ - 7) < 0;
  #      if ( !(v17 ^ v18) )
  #        goto LABEL_14;
  #    }
  #    v9 = *v2;
  #    v10 = v2[1];
  #    v2 += 2;
  #    v11 = ((v9 & 0xF) << 8) + v10;
  #    v22 = v2;
  #    v12 = v9 >> 4;
  #    v21 = v11;
  #    if ( v11 )
  #    {
  #      v13 = v12 + 1;
  #      v14 = 0;
  #      if ( v13 >= 0 )
  #      {
  #        while ( 1 )
  #        {
  #          ++result;
  #          v15 = v5 + 1;
  #          v16 = *(_BYTE *)((((_WORD)v14 + (_WORD)v11) & 0xFFF) + v4);
  #          *(result - 1) = v16;
  #          *(_BYTE *)(v15 + v4 - 1) = v16;
  #          v5 = v15 & 0xFFF;
  #          if ( ++v14 > v13 )
  #            break;
  #          LOWORD(v11) = v21;
  #        }
  #        v2 = v22;
  #      }
  #      goto LABEL_11;
  #    }
  #    v19 = 1;
  #LABEL_14:
  #    ;
  #  }
  #  while ( !v19 );
  #  return result;
  pass

args = parser.parse_args()

with open(args.input, 'rb') as f:
  count = read32(f)
  for i in range(0, count - 1):
    f.seek(4 + 8 * i)
    a = read32(f)
    b = read32(f)
    c = read32(f)
    length1 = b - a
    length2 = c - b

    print("%d: a: 0x%08X b: 0x%08X length: %d (c: 0x%08X; length: %d)" % (i, a, b, length1, c, length2))

    f.seek(a)
    buf = f.read(length1)

    model_a = os.path.join(args.out, 'model-%d-a.bin' % i)
    with open(model_a, 'wb') as t:
      t.write(buf)

    f.seek(b)
    buf = f.read(length2)

    model_b = os.path.join(args.out, 'model-%d-b.bin' % i)
    with open(model_b, 'wb') as t:
      t.write(buf)

    f.seek(a)

    dword_E6B180 = []
    for j in range(0, length1 // 4):
      dword_E6B180.append(read32(f))

    f.seek(b)

    magic = f.read(4) # [0]
    read32(f) # [4]
    offset = read32(f) # [8]

    if (offset == 0xFFFFFFFF):
      #FIXME!!!
      continue
    
    print("%s / Offset: %d" % (magic, offset))
    
    if (magic == b'Comp'):
      # FIXME: Check offset for some things
      buf = f.read(length2 - 12)
      # Run sub_42D520() on the data
    else:
      f.seek(b)
      buf = f.read(length2)

    out = []
    for j in range(0, length2 // 4):
      # Checks some bitmask wether this part is textured?
      if ( (1 << (31 - (j & 0x1F))) & dword_E6B180[j >> 5] ):
        value = int.from_bytes(buf[4*j:4*j+4], byteorder='big', signed=False)
        if ( (value & 0xFF000000) == 0x0A000000 ):
          #FIXME: sub_447490(v17, v19 & 0xFFFFFF, (char **)v18, (int *)v18 + 1);
          # v17 = length2 // 4
          # v19 = value
          # v18 = &value
          # Call into texture loader?!
          print("Need to load texture %d / %d" % (value & 0xFFFFFF, length2 // 4))
          pass
        elif ( value ):
          out.append(value) # Offset into buf
          print("Appending %d" % value)

    # `out` is send through sub_4485D0
    #FIXME: Does this skip the first element?
    for j in range(0, len(out)):
      v = out[j]
      if v:
        #sub_4476B0(v)
        vt = int.from_bytes(buf[v:v+4], byteorder='big', signed=False)
        isBad = False
        isBad |= (vt == 20581)
        isBad |= (vt == 20582)
        isBad |= (vt == 53348)
        isBad |= (vt == 53349)
        isBad |= (vt == 20580)
        isBad |= (vt == 12388)
        isBad |= (vt == 53350)
        if isBad:
          print("this is bad.. skipping")
          continue
        print("%d: Type: 0x%08X (%d)" % (v, vt, vt))
      if v == 0xFFFFFFFF:
        break
    #FIXME: Handle "Data" and "Anim" tags etc

    # These are supported tag types?
    # v20 == 1299145836
    #  || v20 == 1416782187
    #  || v20 == 1349477476
    #  || v20 == 1348563572
    #  || v20 == 1399022958
    #  || v20 == 1296133236
    #  || v20 == 1349873776
