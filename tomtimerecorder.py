import datetime

import sqlite3
from flask import Flask, jsonify
import os

from flask import render_template
from flask import request

app = Flask(__name__)

mydir = os.path.dirname(os.path.realpath(__file__))
dbfile = os.path.join(mydir, "tomtimer")
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


## For example: date +%Y-%m-%d-%H-%M-%S
## wget http://neverwinternights2.nl/tomtimer/mytime/`hostname`/`date +%Y-%m-%d-%H-%M-%S`
@app.route('/mytime/<hostname>/<timestring>', methods=["GET"])
def save_time(hostname, timestring):
    try:
        date  = datetime.datetime.strptime(timestring, "%Y-%m-%d-%H-%M-%S")
        now = datetime.datetime.now()
        query = "INSERT INTO tomtimes (hostname, ip, clienttime, hosttime) VALUES (?,?,?,?)"
        c = get_db().cursor()
        c.execute(query, (hostname, request.remote_addr, date, now))
        get_db().commit()
        return jsonify({"result":"ok"})
    except Exception as e:
        return jsonify({"result": "nok", "error": e.message})

@app.route('/')
def hello_world():
    c = get_db().cursor()
    select  = c.execute("SELECT * FROM tomtimes")
    result = select.fetchall()
    names = [description[0] for description in c.description]
    return render_template('results.html', results=result, names=names)

get_db().cursor().execute('CREATE TABLE IF NOT EXISTS tomtimes(id INTEGER PRIMARY KEY, hostname varchar(25), ip varchar(25), clienttime varchar(25), hosttime varchar(25)')

if __name__ == '__main__':
    app.run()
