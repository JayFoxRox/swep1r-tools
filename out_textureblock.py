#!/usr/bin/env python3

import sys
from PIL import Image

def read8(f):
  return f.read(1)[0]
def read16(f):
  return int.from_bytes(f.read(2), byteorder='big', signed=False)
def read32(f):
  return int.from_bytes(f.read(4), byteorder='big', signed=False)

with open(sys.argv[1], 'rb') as f:


  tags = open("/tmp/swep1r/wxhexeditor.tags", "w")

  tags.write('<?xml version="1.0" encoding="UTF-8"?>\n' + '<wxHexEditor_XML_TAG>\n' + '  <filename>\n')
  tag_id = 0
  def add_tag(start, size, text, colour = "#888888", dump=False):
    global tag_id
    tag_id += 1
    s = ''
    s += '    <TAG id="%s">\n' % tag_id
    s += '      <start_offset>%d</start_offset>\n' % start
    s += '      <end_offset>%d</end_offset>\n' % (start + size - 1)
    s += '      <tag_text>%s (%d bytes)</tag_text>\n' % (text, size)
    s += '      <font_colour>#000000</font_colour>\n'
    s += '      <note_colour>%s</note_colour>\n' % colour
    s += '    </TAG>\n'
    tags.write(s)
    if dump:
      off = f.tell()
      f.seek(start)
      buf = f.read(size)
      with open('/tmp/swep1r/%s.bin' % text, 'wb') as t:
        t.write(buf)
      f.seek(off)
      


  count = read32(f)
  add_tag(0, 4, 'count', '#FF88FF')

  add_tag(4 + 8 * count, 4, 'end-of-table', '#8888FF')

  for i in range(0, count):
    f.seek(4 + 8 * i)
    a = read32(f)
    b = read32(f)
    c = read32(f)
    length = c - a

    print("%d: a: 0x%08X b: 0x%08X (c: 0x%08X; length: %d or %d bytes)" % (i, a, b, c, b - a, length))

    add_tag(4 + 8 * i, 8, 'table-%d' % i)
    if b == 0:
      add_tag(a, c - a, 'tex-%d' % i, "#FFFF88", dump=True)
    else:
      add_tag(a, b - a, 'tex-a-%d' % i, "#FF8888", dump=True)
      add_tag(b, c - b, 'tex-b-%d' % i, "#88FF88", dump=True)


    pixelformat = 8888
    ignore_size = False
    levels = 1

    if b != 0:

      # No idea what section b contains, but hope is that it holds
      # format and resolution information.

      b_size = c - b
      print("Section-b: %d bytes" % (b_size))
      assert((b_size == 32) or (b_size == 512))
      #FIXME: Fix this codepath
      
      length = b - a

      #FIXME: I assumed that section b is a palette, but this does not seem to be true
      palette = False

      if length == 32:
        width = 8
        height = 8
        pixelformat = 4
      elif length == 64:
        width = 8
        height = 8
        pixelformat = 8
      elif length == 128:
        width = 32 // 8
        height = 32 // 4
      elif length == 256:
        width = 16
        height = 32
        pixelformat = 4
      elif length == 512:
        width = 32
        height = 32
        pixelformat = 4
      elif length == 752:
        width = 16
        height = 47
        pixelformat = 8
      elif length == 1024:
        width = 32
        height = 64
        pixelformat = 4
      elif length == 1216:
        width = 32
        height = 38
        pixelformat = 8
      elif length == 1392:
        width = 16
        height = 87
        pixelformat = 8
      elif length == 1400:
        width = 8
        height = 175
        pixelformat = 8
      elif length == 1504:
        width = 32
        height = 47
        pixelformat = 8
      elif length == 1880:
        width = 8
        height = 235
        pixelformat = 8
      elif length == 2048:
        width = 32
        height = 64
        pixelformat = 8
      elif length == 2800:
        width = 64
        height = 32
        levels = 3 #FIXME: Is this correct?!
        ignore_size = True #FIXME: Fix this if the texture has mipmaps?!
        pixelformat = 8
      elif length == 4096:
        # Some of these are 64*16, others seem to be 32x32
        width = 32 * 2
        height = 32 // 2
        #width = 32
        #height = 32
      else:
        assert(False)

      if False:
        pass
      elif i == 157: # Sun?
        width = 64
        height = 64
        pixelformat = 4
        assert(b_size == 32)
      elif i == 158: # Unknown
        width = 16
        height = 128
        pixelformat = 4
      elif i == 159: # Engine texture?
        width = 32
        height = 64
        pixelformat = 4
      else:
        pass

        # Enable the following line if you only want to export known textures
        # Disable it to export all textures
        continue

    else:

      palette = False

      # This is a list of texture resolution / formats.
      # We are currently not sure where the game stores this information.
      if False:
        pass
      elif i == 35: # Landscape?
        width = 64
        height = 32
        pixelformat = 4
      elif i == 103: # Dust / Fog?
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 105: # Shadow
        width = 16
        height = 128
        pixelformat = 4
      elif i == 106: # Shadow
        width = 32
        height = 64
        pixelformat = 4
      elif i == 116: # Fireballs
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 117: # Fireball
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 118: #
        width = 64
        height = 64
        pixelformat = 4
      elif i == 143: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 144: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 183: # Shadow
        width = 32
        height = 64
        pixelformat = 4
      elif i == 184: # Shadow
        width = 32
        height = 128
        pixelformat = 4
      elif i == 224: # Shadow
        width = 32
        height = 64
        pixelformat = 4
      elif i == 225: # Shadow
        width = 32
        height = 64
        pixelformat = 4
      elif i == 229: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 230: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 291: # Shadow
        width = 64
        height = 64
        pixelformat = 4
      elif i == 292: # Shadow
        width = 32
        height = 64
        pixelformat = 4
      elif i == 318: # Shadow
        width = 32
        height = 64
        pixelformat = 4
      elif i == 319: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 340: # Pink plasma animation
        width = 64
        height = 16
        pixelformat = 8888
      elif i == 350: # Shadow
        width = 64
        height = 64
        pixelformat = 4
      elif i == 351: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 378: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 379: # Shadow
        width = 32
        height = 32
        pixelformat = 8       
      elif i == 406: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 407: # Shadow
        width = 32
        height = 64
        pixelformat = 4
      elif i == 435: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 436: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 464: # Shadow
        width = 32
        height = 64
        pixelformat = 4
      elif i == 465: # Shadow
        width = 32
        height = 64
        pixelformat = 4
      elif i == 494: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 495: # Shadow
        width = 32
        height = 64
        pixelformat = 4
      elif i == 513: # Shadow
        width = 32
        height = 64
        pixelformat = 4
      elif i == 514: # Shadow
        width = 64
        height = 64
        pixelformat = 4
      elif i == 530: # Shadow
        width = 32
        height = 64
        pixelformat = 4
      elif i == 545: # Shadow
        width = 32
        height = 64
        pixelformat = 4
      elif i == 546: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 571: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 572: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 585: # Scratch animation
        width = 64
        height = 128
        pixelformat = 4
      elif i == 594: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 595: # Shadow
        width = 32
        height = 64
        pixelformat = 4
      elif i == 604: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 605: # Shadow
        width = 32
        height = 64
        pixelformat = 4
      elif i == 618: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 619: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 626: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 627: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 635: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 636: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 662: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 663: # Shadow
        width = 16
        height = 64
        pixelformat = 4
      elif i == 669: # Pink plasma animation
        width = 64
        height = 16
        pixelformat = 8888
      elif i >= 670 and i <= 678: # Scratch animation
        width = 64
        height = 128
        pixelformat = 4
      elif i == 691: # Cracks
        width = 64
        height = 64
        pixelformat = 4
      elif i == 815: # Pink plasma animation
        width = 64
        height = 16
        pixelformat = 8888
      elif i == 889: # Pink plasma animation
        width = 64
        height = 16
        pixelformat = 8888
      elif i == 923: # Energy wall / plasma?
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 934: # Waterfall texture?
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 936: # Snow, Clouds or Wakes?
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 937: # Red and yellow flag
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 988: # Pink plasma animation
        width = 64
        height = 16
        pixelformat = 8888
      elif i == 1002: # Yellowish cloud?
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 1077: # Smoke?
        width = 8
        height = 32
        pixelformat = 8888
      elif i == 1078: # Pink plasma sparks?
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 1101: # Circle pattern
        width = 64
        height = 64
        pixelformat = 8
      elif i == 1167: # Smoke?
        width = 8
        height = 32
        pixelformat = 8888
      elif i == 1177: # Wall with rivets?!
        width = 64
        height = 32
        levels = 3 #FIXME: Is this correct?!
        ignore_size = True #FIXME: Fix this if the texture has mipmaps?!
        pixelformat = 8
      elif i == 1181: # Wall with rivets?!
        width = 32
        height = 64
        pixelformat = 8
      elif i == 1216: # Unknown, wall maybe?
        width = 32
        height = 64
        pixelformat = 8
      elif i == 1218: # Unknown, wall maybe?
        width = 32
        height = 64
        pixelformat = 8
      elif i == 1221: # Smoke texture? (2 textures in atlas?!)
        width = 64
        height = 64
        pixelformat = 8
      elif i == 1222: # Smoke texture? (2 textures in atlas?!)
        width = 64
        height = 64
        pixelformat = 8
      elif i == 1223: # Smoke texture? (2 textures in atlas?!) - same base as 1222 but less smoke
        width = 64
        height = 64
        pixelformat = 8
      elif i == 1224: # Unknown, some wall texture maybe?
        width = 64
        height = 64
        pixelformat = 8
      elif i == 1234: # Some sparks?
        width = 16
        height = 32
        pixelformat = 8888
      elif i == 1237: # Pink plasma sparks?
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 1255: # Pink plasma animation
        width = 64
        height = 16
        pixelformat = 8888
      elif i == 1257: # Blueish cloud?
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 1258: # Blueish cloud?
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 1328: # Plants?
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 1347: # Pink plasma animation
        width = 64
        height = 16
        pixelformat = 8888
      elif i == 1385: # Beams and crate-wall background
        width = 128
        height = 64
        pixelformat = 4
      elif i == 1396: # Film reel
        width = 128
        height = 64
        pixelformat = 4
      elif i == 1411: # Pink plasma
        width = 32
        height = 32
        pixelformat = 8888
      elif i >= 1412 and i <= 1421: # Pink plasma animation
        width = 64
        height = 16
        pixelformat = 8888
      elif i == 1422: # Fire particles
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 1428: # A ring of some sorts
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 1461: # Horizontal stripes?
        width = 32
        height = 32
        pixelformat = 4
      elif i == 1478: # Smudge or something?
        width = 64
        height = 64
        pixelformat = 4
      elif i == 1484: # Waterfall texture?
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 1485: # Empty ???
        width = 16
        height = 16
        pixelformat = 8
      elif i >= 1486 and i <= 1497: # Skybox alpha?
        width = 64
        height = 64
        pixelformat = 8
      elif i >= 1586 and i <= 1595: # Fire animation
        width = 32
        height = 32
        pixelformat = 8888
      elif i == 1583: # "Arts"
        width = 128
        height = 64
        pixelformat = 4
      elif i == 1584: # "LUCAS"
        width = 32
        height = 128
        pixelformat = 4
      elif i == 1585: # Lucasarts logo upside down
        width = 64
        height = 128
        pixelformat = 4
      elif i == 1596: # Energy plasma alpha?!
        width = 128
        height = 16
        pixelformat = 4
      elif i == 1621: # Vignette round
        width = 32
        height = 32
        pixelformat = 4
      elif i == 1622: # Vignette square corner
        width = 16
        height = 16
        pixelformat = 4
      elif i == 1647: # Window / Grill ?!
        width = 64
        height = 64
        pixelformat = 4
      else:
        assert(False)

    bpp = 0
    t_pixelformat = pixelformat
    while t_pixelformat != 0:
      bpp += t_pixelformat % 10
      t_pixelformat //= 10
    if not ignore_size:
      assert((length * 8) == (width * height * bpp))


    # Seek to pixel data and dump out every texture level
    f.seek(a)
    for level in range(0, levels):
      im = Image.new("RGBA", (width, height))
      pixels = im.load()
      for y in range(0, height):
        for x in range(0, width):

          if pixelformat == 4:
            if x % 2 == 0:
              values = f.read(1)[0]
            value = (values >> 4) & 0xF
            values <<= 4
          else:
            value = int.from_bytes(f.read(bpp // 8), byteorder='big', signed=False)


          real_pixelformat = pixelformat
          if palette:
            off = f.tell()
            f.seek(b + value * 2)
            pixel = int.from_bytes(f.read(2), byteorder='big', signed=False)
            real_pixelformat = 565
            f.seek(off)
          else:
            pixel = value

          if real_pixelformat == 4:
            a = pixel * 0x11
            r = 0
            g = 0
            b = 0
          elif real_pixelformat == 8:
            a = pixel
            r = 0
            g = 0
            b = 0
          elif real_pixelformat == 4444:
            a = ((pixel >> 0) & 0xF) * 0x11
            r = ((pixel >> 4) & 0xF) * 0x11
            g = ((pixel >> 8) & 0xF) * 0x11
            b = ((pixel >> 12) & 0xF) * 0x11
          elif real_pixelformat == 5551:
            a = ((pixel >> 0) & 0x1) * 0xFF
            r = ((pixel >> 1) & 0x1F) * 0xFF // 0x1F
            g = ((pixel >> 6) & 0x1F) * 0xFF // 0x1F
            b = ((pixel >> 11) & 0x1F) * 0xFF // 0x1F
          elif real_pixelformat == 1555:
            r = ((pixel >> 0) & 0x1F) * 0xFF // 0x1F
            g = ((pixel >> 5) & 0x1F) * 0xFF // 0x1F
            b = ((pixel >> 10) & 0x1F) * 0xFF // 0x1F
            a = ((pixel >> 15) & 0x1) * 0xFF
          elif real_pixelformat == 565:
            a = 0xFF
            r = ((pixel >> 0) & 0x1F) * 0xFF // 0x1F
            g = ((pixel >> 5) & 0x3F) * 0xFF // 0x3F
            b = ((pixel >> 11) & 0x1F) * 0xFF // 0x1F
          elif real_pixelformat == 8888:
            a = (pixel >> 0) & 0xFF
            b = (pixel >> 8) & 0xFF
            g = (pixel >> 16) & 0xFF
            r = (pixel >> 24) & 0xFF
          else:
            assert(False)
          pixels[x, y] = (r, g, b, a)
      im.save("/tmp/swep1r/texture-%d-%d.png" % (i, level), 'PNG')
      width //= 2
      height //= 2


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

tags.write('  </filename>\n' + '</wxHexEditor_XML_TAG>\n')


