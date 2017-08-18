import datetime

import sqlite3
from flask import Flask, jsonify
import os

from flask import render_template
from flask import request

app = Flask(__name__)

mydir = os.path.dirname(os.path.realpath(__file__))
dbfile = os.path.join(mydir, "tomtimer")

conn = sqlite3.connect(dbfile)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS tomtimes(id INTEGER PRIMARY KEY, hostname varchar(25), ip varchar(25), clienttime varchar(25), hosttime varchar(25))')

## For example: date +%Y-%m-%d-%H-%M-%S
## wget http://neverwinternights2.nl/tomtimer/mytime/`hostname`/`date +%Y-%m-%d-%H-%M-%S`
@app.route('/mytime/<hostname>/<timestring>', methods=["GET"])
def save_time(hostname, timestring):
    try:
        date  = datetime.datetime.strptime(timestring, "%Y-%m-%d-%H-%M-%S")
        now = datetime.datetime.now()
        query = "INSERT INTO tomtimes (hostname, ip, clienttime, hosttime) VALUES (?,?,?,?)"
        c.execute(query, (hostname, request.remote_addr, date, now))
        conn.commit()
        return jsonify({"result":"ok"})
    except Exception as e:
        return jsonify({"result": "nok", "error": e.message})

@app.route('/')
def hello_world():
    c = conn.cursor()
    select  = c.execute("SELECT * FROM tomtimes")
    result = select.fetchall()
    names = [description[0] for description in c.description]
    return render_template('results.html', results=result, names=names)

if __name__ == '__main__':
    app.run()
