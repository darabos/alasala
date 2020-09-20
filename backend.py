import flask
import sqlite3

app = flask.Flask('backend')

def db():
  db = getattr(flask.g, '_database', None)
  if db is None:
    db = flask.g._database = sqlite3.connect('db')
    c = db.cursor()
    for s in '''
    drop table if exists users
    drop table if exists heroes
    create table users (email text, stage int)
    insert into users values ("test", 0)
    create table heroes (hero text, level int, user text)
    insert into heroes values ("cube", 1, "test")
    '''.strip().split('\n'):
      print(s)
      c.execute(s)
  return db

@app.teardown_appcontext
def close_connection(exception):
  db = getattr(flask.g, '_database', None)
  if db is not None:
    db.close()


def query(q, args=()):
  res = db().cursor().execute(q, args)
  return [dict(zip([c[0] for c in res.description], row)) for row in res]

@app.route('/getuserdata')
def getuserdata():
  user = flask.request.args['user']
  progress = query('select * from users where email = ?', (user,))[0]
  heroes = query('select * from heroes where user = ?', (user,))
  return flask.jsonify({'progress': progress, 'heroes': heroes})
