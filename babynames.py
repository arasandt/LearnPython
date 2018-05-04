#!/usr/bin/python
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# Google's Python Class
# http://code.google.com/edu/languages/google-python-class/

import sys
import os
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup as BS

"""Baby Names exercise

Define the extract_names() function below and change main()
to call it.

For writing regex, it's nice to include a copy of the target
text for inspiration.

Here's what the html looks like in the baby.html files:
...
<h3 align="center">Popularity in 1990</h3>
....
<tr align="right"><td>1</td><td>Michael</td><td>Jessica</td>
<tr align="right"><td>2</td><td>Christopher</td><td>Ashley</td>
<tr align="right"><td>3</td><td>Matthew</td><td>Brittany</td>
...

Suggested milestones for incremental development:
 -Extract the year and print it
 -Extract the names and rank numbers and just print them
 -Get the names data into a dict and print it
 -Build the [year, 'name rank', ... ] list and print it
 -Fix main() to use the extract_names list
"""

def extract_names(filename):
  """
  Given a file name for baby.html, returns a list starting with the year string
  followed by the name-rank strings in alphabetical order.
  ['2006', 'Aaliyah 91', Aaron 57', 'Abagail 895', ' ...]
  """
  # +++your code here+++
  return


def main():
  # This command-line parsing code is provided.
  # Make a list of command line arguments, omitting the [0] element
  # which is the script itself.
  args = sys.argv[1:]

  #if not args:
  #  print 'usage: [--summaryfile] file [file ...]'
  #  sys.exit(1)

  # Notice the summary flag and remove it from args if it is present.
  summary = False
  #if args[0] == '--summaryfile':
  #  summary = True
  #  del args[0]

  # +++your code here+++
  # For each filename, get the names, then either print the text output
  # or write it to a summary file
  #html = urllib2.urlopen(your_site_here)
  #soup = BS(html)
  #elem = soup.findAll('a', {'title': 'title here'})
  #elem[0].text

  whole_files = [os.path.abspath(f) for f in os.scandir(os.getcwd() + '\\' + 'babynames\\') if f.is_file() if str(f.name).find(".html") != -1]
  #print(whole_files)
  for f in whole_files:
  	  #print(f)
  	  soup = BS(open(f),"html5lib")
  	  header = soup.find_all('th')
  	  para = []
  	  for x in header:
  	  	para.append(str(x))

  	  #print(para)
  	  sp1 = [l.split('>')[1] for l in [l.split('</th>')[0] for l in para]]

  	  #print(sp1)

  	  detail = soup.find_all('tr')
  	  row = []
  	  for x in detail:
  	  	row.append(str(x))

  	  print(row[88])
  	  #sp2 = [l.split('</td>')[0] for l in [l.split('<tr align="right"><td>')[1] for l in row]]
  	  sp2 = [l.split('<td>')[1] for l in row]
  	  #sp2 = row[88].split("<td>")
  	  #l = ['element1\t0238.94', 'element2\t2.3904', 'element3\t0139847']
  	  #print(type(l[0]))
  	  #a = [i.split('\t', 1)[0] for i in l]
  	  #print(a)
  	  print(sp2)  	  


  	  break
            #content = file.read()
      #content1 =  [l.split('</td>\n') for l in content.split('<tr align="right"><td>') ]
      #print(content1[-10:-1])
   
  
if __name__ == '__main__':
  main()
