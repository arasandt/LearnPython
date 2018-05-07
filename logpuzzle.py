#!/usr/bin/python
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# Google's Python Class
# http://code.google.com/edu/languages/google-python-class/

import os
import re
import sys
import urllib
import urllib.request
from urllib.parse import urljoin
from operator import itemgetter, attrgetter
"""Logpuzzle exercise
Given an apache logfile, find the puzzle urls and download the images.

Here's what a puzzle url looks like:
10.254.254.28 - - [06/Aug/2007:00:13:48 -0700] "GET /~foo/puzzle-bar-aaab.jpg HTTP/1.0" 302 528 "-" "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6"
"""


def read_urls(filename):
  """Returns a list of the puzzle urls from the given log file,
  extracting the hostname from the filename itself.
  Screens out duplicate urls and returns the urls sorted into
  increasing order."""
  #pass
  with open(filename,'r') as fi:
    content = fi.read()
  get_url = 'http://' + os.path.basename(filename).split('_')[1]
  #print(get_url)
  #sys.exit(1)
  #content_urls = re.findall(r'GET.*google.*HTTP',content)
  content_urls = [f.split(' ')[1] for f in re.findall(r'GET.*puzzle.*HTTP',content)]
  #print(content_urls)
  content_dict = {}
  for f in content_urls:
    sort_key = os.path.splitext(f)[0][-4:]
    #print(sort_key)
    content_dict[sort_key] = urljoin(get_url,f)
    #print(content_dict[f[-10:]] )
    #break
    #print(f[-10:])
  #print(content_dict)
  content_dict_f = [b for a,b in sorted(content_dict.items(),key=itemgetter(0))]
  #print(type(content_dict))
  #print(content_dict_f)
  return content_dict_f
  # +++your code here+++
  

def download_images(img_urls, dest_dir):
  """Given the urls already in the correct order, downloads
  each image into the given directory.
  Gives the images local filenames img0, img1, and so on.
  Creates an index.html in the directory
  with an img tag to show each local image file.
  Creates the directory if necessary.
  """
  #print(os.path.abspath(os.path.join(dest_dir,os.path.basename(img))))
  os.makedirs(dest_dir, exist_ok=True)
  #print(len(img_urls))
  k = 1
  pics = []
  print('Total # of images: ' + str(len(img_urls)))
  for img in img_urls:
    pics.append('img' + str(k))
    local_filename = os.path.abspath(os.path.join(dest_dir,pics[-1]))

    k += 1
    if not os.path.isfile(local_filename):
      print('Retrieving.......  ' + img)
      urllib.request.urlretrieve(img,local_filename)
  
  with open(os.path.join(dest_dir,'index.html'),'w') as f:
# <verbatim>
# <html>
# <body>
# <img src="/edu/python/exercises/img0"><img src="/edu/python/exercises/img1"><img src="/edu/python/exercises/img2">...
# </body>
# </html>
    f.write("<verbatim>")
    f.write("<html>")
    f.write("<body>")
    #for img in img_urls
    for p in pics:
      f.write("<img src=" + str(p)+ ">")
    f.write("<img src>")
    f.write("</body>")
    f.write("</html>")

  # +++your code here+++
  

def main():
  args = sys.argv[1:]
 #print(args)

  if not args:
    print('usage: [--todir dir] logfile ')
    sys.exit(1)

  todir = ''
  if args[0] == '--todir':
    todir = args[1]
    del args[0:2]

  img_urls = read_urls(args[0])
  #print(args)
  #print(todir)

  if todir:
    download_images(img_urls, todir)
  else:
    print('\n'.join(img_urls))

if __name__ == '__main__':
  main()
