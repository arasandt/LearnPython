#!/usr/bin/python
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# Google's Python Class
# http://code.google.com/edu/languages/google-python-class/

import sys
import re
import os
import shutil
#import commands

"""Copy Special exercise
"""

# +++your code here+++
# Write functions and modify main() to call them
def get_special_paths(passdir):
  if passdir == ".":
      wkdir = os.getcwd() + "\\copyspecial"
  else:
      wkdir = passdir
  #special_files = 
  special_files = [f.group() for f in [re.match(re.compile(r'^[a-zA-Z0-9]+__[a-zA-Z0-9]+__\..*$'),f.name ) for f in os.scandir(wkdir) if f.is_file()] if f is not None]
  special_files = [wkdir + "\\" + f for f in special_files]
  #print(special_files)
  return special_files

def copy_to(paths, dir):
  os.makedirs(dir, exist_ok=True)
  for f in paths:
    shutil.copy(f,dir)
  #pass
  return

def zip_to(paths, zippath):
  pass
  return

def main():
  # This basic command line argument parsing code is provided.
  # Add code to call your functions below.

  # Make a list of command line arguments, omitting the [0] element
  # which is the script itself.
  args = sys.argv[1:]
  #print(args)
  if not args:
    print("usage: [--todir dir][--tozip zipfile] dir [dir ...]");
    sys.exit(1)

  # todir and tozip are either set from command line
  # or left as the empty string.
  # The args array is left just containing the dirs.
  todir = ''
  if args[0] == '--todir':
    todir = args[1]
    del args[0:2]

  tozip = ''
  if args[0] == '--tozip':
    tozip = args[1]
    del args[0:2]

  if len(args) == 0:
    print("error: must specify one or more dirs")
    sys.exit(1)
  #print(args)
  # # +++your code here+++
  # # Call your functions
  paths = get_special_paths(args[0])
  if todir:
    copy_to(paths,todir)
  elif tozip:
    zip(paths,tozip)
  else:
    print(paths)


if __name__ == "__main__":
  main()
