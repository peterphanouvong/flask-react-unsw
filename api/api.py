import time
from bs4 import BeautifulSoup
from flask_restplus import Resource, Api, fields, reqparse, inputs
from requests import get
from flask import Flask
import sqlite3
import json
import pandas as pd
from pandas.io import sql
import re


app = Flask(__name__, static_folder="../flask-react-unsw/build", static_url_path='/')
api = Api(app, version='1.0', title='UNSW API', description='just an api for the UNSW courses')

search_parser = reqparse.RequestParser()
search_parser.add_argument('query', type=str)

class_parser = reqparse.RequestParser()
class_parser.add_argument('class', type=str)


def read_from_sqlite(database_file, table_name):
  conn = sqlite3.connect(database_file)
  return sql.read_sql('select * from ' + table_name, conn)


@app.route('/')
def index():
  return app.send_static_file('index.html')


@api.route('/api/courses')
class Courses(Resource):
  @api.response(200, 'OK')
  @api.response(201, 'Created')
  @api.response(400, 'Bad Request')
  @api.response(404, 'Not Found')
  @api.expect(search_parser)
  def get(self):
    query_str = search_parser.parse_args().get('query')

    df = read_from_sqlite('unsw.db', 'courses')
    df.drop_duplicates(subset="code", keep=False, inplace=True)
    df.set_index('code', inplace=True)

    if query_str is None:
      return {"courses": df.to_dict('index')}

    filtered_df = df[
        df.index.str.contains(query_str, flags=re.IGNORECASE)]

    return {"courses": filtered_df.to_dict('index')}


@api.route('/api/classes')
class Classes(Resource):
  @api.response(200, 'OK')
  @api.response(201, 'Created')
  @api.response(400, 'Bad Request')
  @api.response(404, 'Not Found')
  @api.expect(class_parser)
  def get(self):
    classCode = class_parser.parse_args().get('class')
    res = get('https://www.handbook.unsw.edu.au/undergraduate/courses/2020/{}'.format(classCode))
    if res.status_code != 200:
      res = get('https://www.handbook.unsw.edu.au/postgraduate/courses/2020/{}'.format(classCode))
      if res.status_code != 200:
        return api.abort(404, "Not Found")

    soup = BeautifulSoup(res.text, 'html.parser')
    description = soup.find('div', {'class': 'readmore__wrapper'}).text
    print(description)
    readMoreSubjectConditions = soup.find('div', {'id': 'readMoreSubjectConditions'})
    if readMoreSubjectConditions != None:
      conditions = readMoreSubjectConditions.find('div').find('div').text
      print(conditions)
    else:
      conditions = "No Prerequisite conditions"
    title = soup.find('span', {'data-hbui': 'module-title'}).text

    return {
        "description": description,
        "conditions": conditions,
        "title": title,
        "code": classCode
    }


@app.route('/api/courses/<course>/<term>')
def getCourses(course, term):
  url = "http://classutil.unsw.edu.au/{}_{}.html".format(course, term)
  response = get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  courses = []
  d = soup.findAll("tr", {"class": "cufatrow"})
  for a in d:
    children = a.findAll("td", recursive=False)
    for c in children:
      b = c.find("a", recursive=False)
      if b != None:
        courses.append(b.text)

  return {"courses": courses}
