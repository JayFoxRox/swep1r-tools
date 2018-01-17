#!/usr/bin/env python3

import sys

from arguments import multiparser

strings = {}

args = multiparser.parse_args()

for path in args.input:
  with open(path, 'rb') as in_file:
    data = in_file.read()
    
    # FIXME: Make sure first 4 bytes are not 'ENCR' or decrypt file

    cursor = 0
    while(cursor < len(data)):
      start = cursor

      # Find end of this entry
      while(cursor < len(data)):
        if (data[cursor] == 10 or data[cursor] == 13):
          break
        cursor += 1
      end = cursor

      sep = data.find(9, start)
      key = data[start:sep]
      value = data[sep + 1:end]
      if key in strings:
        print("Warning: duplicate key " + str(key), file=sys.stderr)
      strings[key] = value

      # Move to next entry
      while(cursor < len(data)):
        if (data[cursor] != 10 and data[cursor] != 13):
          break
        cursor += 1

for key in strings:
  value = strings[key].decode('windows-1252')
  key = key.decode('ascii')
  print("'" + key + "'  ->  '" + value + "'")
