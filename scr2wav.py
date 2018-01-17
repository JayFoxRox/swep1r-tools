#!/usr/bin/env python3

# The demo version of Star Wars Episode 1: Racer uses a messed up file format for audio.
# Basically it's just XOR'd with 0x55, 0x55, 0xEE, 0xEE and the name Caesar shifted.
# This script undoes this mess, but the files will still be suffix'd with ".rbq"

import os

from arguments import multiparser

args = multiparser.parse_args()

for path in args.input:
  filename = os.path.basename(path)
  real_filename = ''
  for s in filename:
    c = ord(s)
    if (c >= ord('a') and c <= ord('z')):
      c = ((c - ord('a') + 25) % 26) + ord('a')
    if (c >= ord('A') and c <= ord('Z')):
      c = ((c - ord('A') + 25) % 26) + ord('A')
    real_filename += '%c' % c
  print("Processing %s (%s)" % (filename, real_filename))
  with open(path, 'rb') as in_file:
    with open(real_filename, 'wb') as out_file:
      data = in_file.read()
      real_data = bytes([data[i] ^ (0x55 if ((i % 4) <= 1) else 0xEE) for i in range(len(data))])
      out_file.write(real_data)
