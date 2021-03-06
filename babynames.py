#!/usr/bin/python
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# Google's Python Class
# http://code.google.com/edu/languages/google-python-class/

import sys
import msvcrt
import os
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
from operator import itemgetter, attrgetter
from collections import OrderedDict

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

def extract_names(f):

    """
    Given a file name for baby.html, returns a list starting with the year string
    followed by the name-rank strings in alphabetical order.
    ['2006', 'Aaliyah 91', Aaron 57', 'Abagail 895', ' ...]
    """
    # +++your code here+++
    fil = str(os.path.basename(f)).split('.')[0][4:]
    sp5=[]
    soup = BS(open(f),"html5lib")
    header = soup.find_all('th')
    #para = []
    para = [str(x) for x in header]
    
    #for x in header:
    #    para.append(str(x))
    #print(para)

    sp1 = [l.split('>')[1] for l in [l.split('</th>')[0] for l in para]]


    #detail = soup.find_all(re.compile(r'<tr align="right"><td>(\d+)</td><td>(\w+)</td><td>(\w+)</td>'))
    detail = soup.find_all(re.compile(r"tr"))
    detail1 = re.findall(r'<td>(\d+)</td><td>(\w+)</td>\<td>(\w+)</td>', str(detail))
    #print(detail1)
    #row = []
    #row = [str(y) for y in detail if str(y).find('<tr align="right"><td>') != -1]
    #for y in detail:
    #    if str(y).find('<tr align="right"><td>') != -1: #and str(y).find('</td><td>') != -1 :
    #        row.append(str(y))
    #print(row)
    #sys.exit(1)
    #row = row[1:]
    #sp2 = [l.split('</td>')[0] for l in [l.split('<tr align="right"><td>')[1] for l in row]]
    #sp3 = [l.split('<td>')[1] for l in [l.split('</td>')[1] for l in row]]
    #sp4 = [l.split('<td>')[1] for l in [l.split('</td>')[2] for l in row]]
    #sp5 = sp5 + list(zip(sp2,sp3))
    #sp5 = sp5 + list(zip(sp2,sp4))
    #final_temp = sorted(sp5,key=itemgetter(1))
    #print(detail1)
    #sys.exit(1)
    wk_dict = {}
    for tuples in detail1:
        (rank,boyname,girlname) = tuples
        if boyname not in wk_dict:
            wk_dict[boyname] = rank
        if girlname not in wk_dict:
            wk_dict[girlname] = rank


 


    wk_dict1 = sorted(wk_dict.items(), key=itemgetter(0))
    #print(wk_dict1)
    names = []
    for name in wk_dict1:
        (a , b) = name
        names.append(a + " " +b)
    #print(wk_dict)
    # sys.exit(1)
    # final_temp = sorted(detail1,key=itemgetter(1))
    # final_temp = [l[1] + " " + l[0] for l in final_temp ]
    # final = []
    # for i in final_temp:
    #    final.append(i)
    #     if str(final[-2:-1:]).split(' ')[0] == str(final[-1:]).split(' ')[0]:
    #         if str(final[-2:-1:]).split(' ')[1] < str(final[-1:]).split(' ')[1]:
    #             final = final[:-1:]
    #         else:
    #             final = final[:-2:] + final[-1:]
    # #print(fil)

    #ab = '\n'.join(names)
    #for i in final:
    #print(final)
    #print('\n'.join(names))



    return ('\n'.join(names),fil)


def main():
    # This command-line parsing code is provided.
    # Make a list of command line arguments, omitting the [0] element
    # which is the script itself.
    args = sys.argv[1:]

    if not args:
      print('usage: [--summaryfile] file [file ...]')
      sys.exit(1)

    # Notice the summary flag and remove it from args if it is present.
    #print(args)
    #print(args[1:])
    summary = False
    if args[0] == '--summaryfile':
      summary = True
      del args[0]
    else:
      print('usage: [--summaryfile] file [file ...]')
      sys.exit(1)      

    if not args:  
      print('usage: [--summaryfile] file [file ...]')
      sys.exit(1)
        
    #print(args[0])  
    # +++your code here+++
    # For each filename, get the names, then either print the text output
    # or write it to a summary file
    
    #html = urllib2.urlopen(your_site_here)
    #soup = BS(html)
    #elem = soup.findAll('a', {'title': 'title here'})
    #elem[0].text
    #whole_files = [os.path.abspath(f) for f in os.scandir(os.getcwd() + '\\' + 'babynames\\') if f.is_file() if str(f.name).find(".html") != -1]
    for f in args:
        fil = os.getcwd() + '\\' + f
        #print(fil)
        names,file_name = extract_names(f)
        with open(fil + ".summary",'w') as wr:
            wr.write(file_name + "\n")
            wr.write(names + "\n")
        
    #for f in whole_files:
        #extract_names(f)
    #    print("******************************")
    #    break

    #print(whole_files)
            #content = file.read()
      #content1 =  [l.split('</td>\n') for l in content.split('<tr align="right"><td>') ]
      #print(content1[-10:-1])



if __name__ == '__main__':
    main()
