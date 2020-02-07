from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
import os
import sqlite3

app = Flask(__name__)
s = Session()
app.secret_key = os.urandom(12).hex()


def init_db():
    execute('''create table if not exists task (
    id integer
    constraint task_pk primary key
     autoincrement, 
    txt text,
    done integer
);''')


def execute(query, get=False, params=None):
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    if params:
        c.execute(query, params)
    else:
        c.execute(query)
    if get:
        return c.fetchall()
    else:
        conn.commit()
    conn.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    res = execute('''select * from task''', True)
    out = [[elem for elem in row] for row in res]  # tuple to array
    for row in out:
        row.append("disabled" if row[2] == 1 else "")  # disable editing
        row[2] = "checked" if row[2] == 1 else ""  # and decode sqlite's integer into boolean
    return render_template('index.html', res=out)


@app.route("/api/add")
def add():
    execute('''insert into task ("txt", "done") values ("", 0)''')
    return index()


@app.route("/api/update")
def update():
    row_id = int(request.args.get('id'))
    raw_checked = request.args.get('checked')
    value = request.args.get('value')
    if raw_checked is not None:
        checked = 1 if raw_checked == "true" else 0
        execute('''Update task set done = ? where id = ?''', params=(checked, row_id))
    if value is not None:
        execute('''Update task set txt = ? where id = ?''', params=(value, row_id))
    return index()


@app.route("/api/remove/<int:row_id>")
def remove(row_id):
    execute('''Delete from task where id = ?''', params=(row_id,))
    return index()


if __name__ == "__main__":
    init_db()
    app.debug = True
    app.run()
