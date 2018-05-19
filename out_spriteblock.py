#!/usr/bin/env python3

import sys
from PIL import Image

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

with open(sys.argv[1], 'rb') as f:
  count = read32(f)
  for i in range(0, count):
    f.seek(4 + 4 * i)
    off_a = read32(f)
    off_b = read32(f)
    length = off_b - off_a

    print("%d: a: 0x%08X b: 0x%08X length: %d" % (i, off_a, off_b, length))

    f.seek(off_a)

    width = read16(f)
    print("total width?: %d" % width) # [0]
    height = read16(f)
    print("total height?: %d" % height) # [2]
    fmt = read16(f)
    print("format: 0x%04X" % fmt) # [4]
    unk3 = read16(f)
    assert(unk3 == 0x0000)
    print("always 0: 0x%04X" % unk3) # [6]
    unk4 = read32(f)
    print("palette offset?: 0x%08X" % unk4) # [8]
    unk5 = read16(f) #FIXME: signed!
    print("page count?: 0x%04X" % unk5) # [12]
    unk6 = read16(f)
    assert(unk6 == 0x0020)
    print("always 32: 0x%04X" % unk6) # [14]
    unk7 = read32(f)
    print("data offset / header size? [unused?]: 0x%08X" % unk7) # [16]

    # FIXME: This might be bad..
    headsize = 8 * unk5 # (8 * unk5 + 0xF) & 0xFFFFFFF0

    pages = []
    if (unk7 & 0xFF != 2) or unk4:
      print("Load! %d * 8" % unk5)
      f.seek(off_a + 20)
      #buf = f.read(unk5 * 8)
      for j in range(0, unk5):
        page = (read16(f), read16(f), read32(f))
        print("  %d %d %d" % page)
        pages.append(page)

    if (unk4):
      #v22 = (char *)((unsigned int)&v22[v23 + 15] & 0xFFFFFFF0);
      #v23 = *(_DWORD *)(*(_DWORD *)v18 + 4) - v29;
      #count = b + 4 - unk4 # Read a DWORD there?!
      #sub_42D640(1, v29 + v42, v22, count);
      f.seek(off_a + unk4)
      #*v40 = v22
      print("Bad!")
    else:
      print("Good!")

    for j in range(0, unk5):
      f.seek(off_a + headsize)

      #if v32 == v30 - 1:
      #  v33 = v43 - v42
      #else:
      #  v33 = *(_DWORD *)(*(_DWORD *)v18 + 8 * v32 + 12)
      #v34 = *(_DWORD *)(8 * v32 + *(_DWORD *)v18 + 4)
      #v37 = v33 - v34
      #sub_42D640(1, v34 + v42, i, v33 - v34)
      #*(_DWORD *)(8 * v32 + *(_DWORD *)v18 + 4) = i
      #if ( a1 != 99 ):
      #  sub_446B60((int)v38, (char **)(*(_DWORD *)v18 + 8 * v32))
      #v30 = *v41
      #i = (_WORD *)(((unsigned int)i + v37 + 15) & 0xFFFFFFF0)
      

    # Yay for hardcoded shit..
    if i == 99:
      pass #sub_446A20(v38);

    reader = None

    global pixel_palette

    global pixel_index

    def pixel_p8():
      global pixel_palette
      index = f.read(1)[0]
      #print(index)
      return pixel_palette[index]

    def pixel_p4():
      global pixel_palette
      global pixel_value
      global pixel_index
      if pixel_index == 0:
        pixel_value = f.read(1)[0]
      #print(pixel_value)
      #print(pixel_index)
      index = (pixel_value >> (4 * (1 - pixel_index))) & 0xF
      pixel_index += 1
      pixel_index %= 2

      return pixel_palette[index]

    def pixel_a8():
      a = f.read(1)[0]
      return (a, a, a, 255)

    def pixel_a4():
      global pixel_value
      global pixel_index
      if pixel_index == 0:
        pixel_value = f.read(1)[0]
      #print(pixel_value)
      #print(pixel_index)
      a = ((pixel_value >> (4 * (1 - pixel_index))) & 0xF) * 0x11
      pixel_index += 1
      pixel_index %= 2
      return (a, a, a, 255)

    def pixel_a8r8g8b8():
      r = f.read(1)[0]
      g = f.read(1)[0]
      b = f.read(1)[0]
      a = f.read(1)[0]
      return (r, g, b, a)


    if (fmt == 0x0003):
      reader = pixel_a8r8g8b8
    elif (fmt == 0x0400):
      reader = pixel_a4
    elif (fmt == 0x0401):
      reader = pixel_a8
    elif (fmt == 0x0200):
      reader = pixel_p4
      f.seek(off_a + unk4)
      pixel_palette = []
      for j in range(0, 16):
        # Read palette data
        color = int.from_bytes(f.read(2), byteorder='big', signed=False)
        a = (color >> 0) & 0x1
        b = ((color >> 1) & 0x1F) / 0x1F
        g = ((color >> 6) & 0x1F) / 0x1F
        r = ((color >> 11) & 0x1F) / 0x1F
        pixel_palette.append((int(r * 255), int(g * 255), int(b * 255), a * 0xFF))
    elif (fmt == 0x0201):
      reader = pixel_p8
      f.seek(off_a + unk4)
      pixel_palette = []
      for j in range(0, 256):
        # Read palette data
        color = int.from_bytes(f.read(2), byteorder='big', signed=False)
        a = (color >> 0) & 0x1
        b = ((color >> 1) & 0x1F) / 0x1F
        g = ((color >> 6) & 0x1F) / 0x1F
        r = ((color >> 11) & 0x1F) / 0x1F
        pixel_palette.append((int(r * 255), int(g * 255), int(b * 255), a * 0xFF))

    else:
      assert(False)
      continue

    im = Image.new("RGBA", (width, height))
    pixels = im.load()
    x = 0
    y = 0
    prev_page_height = 0
    for j in range(0, len(pages)):
      page = pages[j]

      pixel_index = 0

      page_width = page[0]
      page_height = page[1]
      page_offset = page[2]

      if (x + page_width) > width:
        print("Reached border")
        x = 0
        y += prev_page_height

      if fmt == 0x0201:
        page_width = (page_width + 0x7) & 0xFFFFFFF8
      elif fmt == 0x0400:
        page_width = (page_width + 0xF) & 0xFFFFFFF0
      elif fmt == 0x0200:
        page_width = (page_width + 0xF) & 0xFFFFFFF0
      elif fmt == 0x0401:
        page_width = (page_width + 0x7) & 0xFFFFFFF8
      elif fmt == 0x0003:
        pass
        #page_width = (page_width + 0xF) & 0xFFFFFFF0
      else:
        print("Unknown format: 0x%04X" % fmt)
        assert(False)

      im_page = Image.new("RGBA", (page_width, page_height))
      pixels_page = im_page.load()

      f.seek(off_a + page_offset)

      print("Drawing page (%d x %d) at %d, %d from %d" % (page_width, page_height, x, y, f.tell()))

      for page_y in range(0, page_height):
        for page_x in range(0, page_width):
          r, g, b, a = reader()
          #print(page_x)
          #print(page_y)
          pixels_page[page_x, page_y] = (r, g, b, a)

          abs_x = x + page_x
          abs_y = y - page_y + page_height - 1
          if (abs_x < width):
            if (abs_y < height):
              pixels[abs_x, abs_y] = (r, g, b, a)

      x += page_width
      prev_page_height = page_height



      #im_page.save("/tmp/swep1r/sprite-%d_%d-0x%04X.png" % (i, j, fmt), 'PNG')

    im.save("/tmp/swep1r/sprite-%d.png" % i, 'PNG')
