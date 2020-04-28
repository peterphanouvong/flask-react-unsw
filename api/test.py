from bs4 import BeautifulSoup
from requests import get
import pandas as pd
import sqlite3
from pandas.io import sql


def write_in_sqlite(dataframe, database_file, table_name):
    conn = sqlite3.connect(database_file)
    dataframe.to_sql(name=table_name, con=conn, if_exists='replace')


def read_from_sqlite(database_file, table_name):
    conn = sqlite3.connect(database_file)
    return sql.read_sql('select * from ' + table_name, conn)

# get all the course categories
def getAllCategories(): 
  #id = 0
  res = get('http://timetable.unsw.edu.au/2020/subjectSearch.html')
  soup = BeautifulSoup(res.text, 'html.parser')

  courses = []
  table_data = soup.findAll("td", {"class": "data"})
  for t in table_data:
    course = t.find("a", recursive=False, href=True)
    if course != None:
      courses.append(course)

  courses_2 = []
  i = 0
  while i in range(len(courses)-2):
    obj = {
      "category" : courses[i].text,
      "name" : courses[i+1].text,
      "url" : courses[i]['href'],
      #"id" : id
    }
    #id += 1
    courses_2.append(obj)
    i += 2

# get all the courses for a couse category
def getAllCourses(code):
  res = get('http://timetable.unsw.edu.au/2020/{}KENS.html'.format(code))
  soup = BeautifulSoup(res.text, 'html.parser')

  courses_init = []
  table_data = soup.findAll("td", {"class": "data"})
  for t in table_data:
    course = t.find("a", recursive=False, href=True)
    if course != None:
      courses_init.append(course.text)
  courses_init = courses_init[5:-1]
  courses_init.remove('Back to top')
  
  courses_final = []
  i = 0
  while i in range(len(courses_init)-2):
    obj = {
      "code" : courses_init[i],
      "name" : courses_init[i+1],
    }
    courses_final.append(obj)
    i += 2
  
  return pd.DataFrame(courses_final)

def getClass(classCode):
  res = get('https://www.handbook.unsw.edu.au/undergraduate/courses/2020/{}'.format(classCode))
  soup = BeautifulSoup(res.text, 'html.parser')
  description = soup.find('div', {'class' : 'readmore__wrapper'}).text
  print(description)

  conditions = soup.find('div', {'id' : 'readMoreSubjectConditions'}).find('div').find('div').text
  print(conditions)

  return {
    "description" : description,
    "conditions" : conditions
  }
  

if __name__ == '__main__':
  getClass('COMP2121')