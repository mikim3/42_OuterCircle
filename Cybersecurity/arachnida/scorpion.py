#!/usr/bin/env python3
import sys
from PIL import Image
from PIL.ExifTags import TAGS

def print_metadata(filename):
  print(f"==> Metadata for {filename}:")
  try:
    with Image.open(filename) as img:
      exif_data = img._getexif()
      if exif_data is not None:
        for tag_id, value in exif_data.items():
          tag_name = TAGS.get(tag_id, tag_id)
          print(f"  {tag_name}: {value}")
      else:
        print("  No EXIF metadata found.")
  except Exception as e:
    print(f"  Error reading {filename}: {e}")

def main():
  if len(sys.argv) < 2:
    print("Usage: ./scorpion FILE1 [FILE2 ...]")
    sys.exit(1)

  for f in sys.argv[1:]:
    print_metadata(f)

if __name__ == '__main__':
  main()
