# python3 -m venv .venv
# source .venv/bin/activate
# python3 -m pip install beautifulsoup4 requests pandas

from bs4 import BeautifulSoup
import re #re is the default regex module for Python
import requests
import pandas as pd

# getting a copy of the underlying HTML file from this URL
html = requests.get("http://timetable.unsw.edu.au/2020/INFS2822.html").text
# soup is the common naming convention of a BeautifulSoup object
# A BeautifulSoup object contains all the HTML, in a special 'tree' like data structure
# You can also think of it as a 'soup' of tags: 
# Parsing will convert the raw HTML file to this 'nested tree' data structure
# This is important because we can then access specific tags within the HTML
soup = BeautifulSoup(html, 'html.parser')

# find and findAll methods in BS4 enable us to filter a HTML page to find a tag or list of desired tags
# findAll- give you all instances, find = only the first instance

'''find_all(tag, attributes, recursive, text, limit, keywords)
find(tag, attributes, recursive, text, keywords)'''
# So we can pass a list of HTML tags (such as h1, h2, div etc), or we can pass an attribute (e.g. 'class':{'red'},
# or we can pass a text argument.)

'''Regular expressions are used to identify regular strings. You use a list of symbols to match a string.
Based on the symbols, either the string will match, so you will keep it, or if the string doesn't match,
you'll ignore it.'''
t3headings = soup.body.findAll(text=re.compile('SUMMARY OF TERM THREE CLASSES'))
print(t3headings)
t3heading = t3headings[0]

t3headingtable = t3heading.parent.parent.parent
print(t3headingtable) 

# Actual data is on next table structure
# the table elements here are siblings as they are at the same level
t3classes_megatable = t3headingtable.findNext("table")
t3classes_megatable_tr = t3classes_megatable.findChildren()[0]
t3classes_megatable_td = t3classes_megatable_tr.findChildren()[0]
# only find children that are immediate children 
t3classes_children = t3classes_megatable_td.findChildren(recursive=False)
t3classes_datatable = t3classes_children[3]
print(t3classes_datatable)

# https://stackoverflow.com/a/50633450
# essentially a common approach to extract all the data from a table
l = []
for tr in t3classes_datatable.find_all('tr'):
    # td stores a list of all the td elements
    td = tr.find_all('td')
    # we call the .text attribute
    # this gets rid of the HTML tags that we don't want
    row = [tr.text for tr in td]
    # the notation on line 62 is 'list comprehension'
    l.append(row)
df = pd.DataFrame(l)

print(df)

df.to_csv("out.csv")