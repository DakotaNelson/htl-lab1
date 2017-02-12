"""
A Flask server that presents a minimal browsable interface for the Olin course catalog.

author: Oliver Steele <oliver.steele@olin.edu>
date  : 2017-01-18
license: MIT
"""

import os

import pandas as pd
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

courses = pd.read_csv('./data/olin-courses-16-17.csv')

def split_names(namestring):
    # first, split multi-name strings with semicolons
    names = namestring.split("; ")

    ret =[]
    for name in names:
        ret.append(" ".join(list(reversed(name.split(", ")))))

    return " ".join(ret)

# make the names not be reversed
courses["course_contact"] = courses["course_contact"].dropna().apply(
        # something something readability of oneliners?
        lambda name: split_names(name)
)

@app.route('/health')
def health():
    return 'ok'

@app.route('/')
def home_page():
    return render_template('index.html', areas=set(courses.course_area), contacts=set(courses.course_contact.dropna()))

@app.route('/instructor/<string:lastname>')
def courses_by_instructor(lastname):
    # pretty ugly hack to deal with case sensitivity
    localCourses = courses.copy(deep=True)
    localCourses["course_contact"] = localCourses["course_contact"].dropna().apply(
            lambda name: name.lower()
    )
    ret = courses.loc[localCourses["course_contact"].str.contains(lastname.lower()).fillna(value=False)]
    return render_template('course_area.html', courses=ret.iterrows())

@app.route('/area/<course_area>')
def area_page(course_area):
    return render_template('course_area.html', courses=courses[courses.course_area == course_area].iterrows())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    production = bool(os.environ.get('PRODUCTION', False))
    if production:
        host = '0.0.0.0'
    else:
        host = '127.0.0.1'

    app.run(host=host, debug=True, port=port)
