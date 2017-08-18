import datetime

import sqlite3
from flask import Flask, jsonify
import os

from flask import g
from flask import render_template
from flask import request

app = Flask(__name__)
mydir = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(mydir, "tomtimer")

def get_db(database_name):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database_name)
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
        query = 'INSERT INTO tijdregistratie (hostnaam, systeemtijd_client, systeemtijd_server, ip_nummer) VALUES (?,?,?,?)'
        c = get_db(DATABASE).cursor()
        c.execute(query, (hostname, date, now, request.remote_addr))
        get_db(DATABASE).commit()
        return jsonify({"result":"ok"})
    except Exception as e:
        return jsonify({"result": "nok", "error": e.message})

@app.route('/')
def hello_world():
    c = get_db(DATABASE).cursor()
    select  = c.execute("SELECT * FROM tijdregistratie")
    result = select.fetchall()
    names = [description[0] for description in c.description]
    return render_template('results.html', results=result, names=names)

with app.app_context():
    get_db(DATABASE).cursor().execute('CREATE TABLE tijdregistratie (hostnaam varchar2(20),systeemtijd_client varchar2(20), systeemtijd_server varchar2(20), ip_nummer varchar2(20))');

if __name__ == '__main__':
    app.run()
