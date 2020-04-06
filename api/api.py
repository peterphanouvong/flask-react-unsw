import time
from bs4 import BeautifulSoup
from requests import get
from flask import Flask
from flask_restplus import Resource, Api, fields, reqparse, inputs
import json
import pandas as pd


app = Flask(__name__)

@app.route('/time')
def get_current_time():
  return {'time': time.time()}


@app.route('/courses/')
def getCourses():
  url = 'http://classutil.unsw.edu.au/COMP_T1.html'
  response = get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  courses = []
  d = soup.findAll("tr", {"class" : "cufatrow"})
  for a in d:
    children = a.findAll("td", recursive=False)
    for c in children:
      b = c.find("a", recursive=False)
      if b != None:
        courses.append(b.text)
  print(courses)

  return {"courses" : courses}