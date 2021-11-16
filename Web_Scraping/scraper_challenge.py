from bs4 import BeautifulSoup
import re
import requests
import pandas as pd
import sys 

courses = sys.argv[1:4]
print(courses)

courselist = []

for course in courses:
    html = requests.get("http://timetable.unsw.edu.au/2020/" + course.upper() + ".html").text
    soup = BeautifulSoup(html, 'html.parser')
    
    t3headings = soup.body.findAll(text=re.compile('SUMMARY OF TERM THREE CLASSES'))
    t3heading = t3headings[0]
    t3headingtable = t3heading.parent.parent.parent
    t3classes_megatable = t3headingtable.findNext("table")
    t3classes_megatable_tr = t3classes_megatable.findChildren()[0]
    t3classes_megatable_td = t3classes_megatable_tr.findChildren()[0]
    t3classes_children = t3classes_megatable_td.findChildren(recursive=False)
    t3classes_datatable = t3classes_children[3]

    # https://stackoverflow.com/a/50633450
    # L list saves data for 1 course, need create multiple dataframes & merge them together
    l = []
    for tr in t3classes_datatable.find_all('tr'):
        td = tr.find_all('td')
        row = [tr.text for tr in td]
        l.append(row)
    
    # create multipledataframes and merge them together
    df = pd.DataFrame(l)

    teachers = []
    t3details = soup.body.findAll(text=re.compile('TERM THREE CLASSES - Detail'))
    t3detail = t3details[0]
    t3details_wrapper = t3detail.parent.parent.parent
    t3teachers_megatable = t3details_wrapper.findNext("table")
    t3teachers_megatable_ch1 = t3teachers_megatable.findChildren(recursive=False)
   
    for child in t3teachers_megatable_ch1:
       grandchildren = child.findChildren(recursive=False)
       for gc in grandchildren:
           form_body = gc.findChildren("td", class_="formBody")
           if len(form_body) > 0:
               for fb in form_body:
                   data_items = fb.findChildren("td", class_="data")
                   if len(data_items) == 5:
                       teacher_data = data_items[4]
                       teachers_list = teacher_data.text.split(",")[0]
                       teachers.append(teachers_list)
   
    # to know which course the data is for
    df['course'] = course

    df['teachers'] = ''.join(list(set(teachers)))
    # append each df to overall list
    courselist.append(df)
    
# list of dataframes, combine them into one df, simple one line
df_all = pd.concat(courselist)
df_all = df_all.dropna() 
df_all = df_all.reset_index()
df_all.columns = ['index', 'Activity', 'Period', 'Class', 'Section', 'Status', 'Enrols/Capacity', 'Day/Start Time', 'Course', 'teacher']
df_all = df_all.loc[df_all['Section'] != 'Section']


print(df_all)
df_all.to_csv("out.csv")