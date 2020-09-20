import flask
import sqlite3

app = flask.Flask('backend')

def init_table(c, test, commands):
  print(query(c, test))
  if not query(c, test):
    for s in commands.strip().split('\n'):
      print(s)
      c.execute(s)

def db():
  db = getattr(flask.g, '_database', None)
  if db is None:
    db = flask.g._database = sqlite3.connect('db')
    c = db.cursor()
    print(query(c, 'select * from users'))
    print(query(c, 'SELECT name FROM sqlite_master WHERE type="table"'))
    init_table(c, 'select * from users where email = "test"', '''
      drop table if exists users
      create table users (email text, stage int, day int)
      insert into users values ("test", 0, 1)
      ''')
    init_table(c, 'select * from heroes where user = "test"', '''
      drop table if exists heroes
      create table heroes (name text, level int, user text)
      insert into heroes values ("cube", 1, "test")
      ''')
  return db.cursor()

@app.teardown_appcontext
def close_connection(exception):
  db = getattr(flask.g, '_database', None)
  if db is not None:
    print('closing db')
    db.commit()
    db.close()

def query(cursor, q, args=()):
  res = cursor.execute(q, args)
  return [dict(zip([c[0] for c in res.description], row)) for row in res]

@app.route('/getuserdata')
def getuserdata():
  user = flask.request.args['user']
  c = db()
  progress = query(c, 'select * from users where email = ?', (user,))[0]
  heroes = query(c, 'select rowid as id, * from heroes where user = ?', (user,))
  return flask.jsonify({'progress': progress, 'heroes': heroes})

@app.route('/searchbeach', methods=['POST'])
def searchbeach():
  user = flask.request.get_json()['user']
  hero = {'name': 'cube', 'level': 1}
  c = db()
  c.execute('update users set day = day + 1 where email = ?', (user,))
  c.execute('insert into heroes values (?, ?, ?)', (hero['name'], hero['level'], user))
  progress = query(c, 'select * from users where email = ?', (user,))[0]
  heroes = query(c, 'select rowid as id, * from heroes where user = ?', (user,))
  return flask.jsonify({'progress': progress, 'heroes': heroes, 'just_found': hero})
