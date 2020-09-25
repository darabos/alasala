import flask
import random
import sqlite3
import backend.battle_simulator as bs
from backend.heroes import Hero

app = flask.Flask('backend')

def init_table(c, test, commands):
  try:
    test_success = query(c, test)
  except sqlite3.OperationalError:
    test_success = False
  if not test_success:
    for s in commands.strip().split('\n'):
      print(s)
      c.execute(s)

def db():
  db = getattr(flask.g, '_database', None)
  if db is None:
    db = flask.g._database = sqlite3.connect('db')
    c = db.cursor()
    init_table(c, 'select * from users where email = "test"', '''
      drop table if exists users
      create table users (email text, stage int, day int, ectoplasm int)
      insert into users values ("test", 0, 1, 0)
      ''')

    init_table(c, 'select * from heroes where user = "test"', '''
      drop table if exists heroes
      create table heroes (name text, level int, user text)
      insert into heroes values ("cube", 1, "test")
      ''')
    print(query(c, 'select * from users'))
    print(query(c, 'SELECT name FROM sqlite_master WHERE type="table"'))
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

@app.route('/computecombat', methods=['POST'])
def computecombat():
  args = flask.request.get_json()
  user = args['user']
  party = args['party']
  stage = args['stage']
  c = db()
  heroes = get_heroes_of_user(c, user)

  def find_hero_by_id(id):
    for h in heroes:
      if h['id'] == id:
        return h

  heroes_in_party = [find_hero_by_id(hero_id) for hero_id in party]
  log = bs.simulate_battle(heroes_in_party, stage)
  winner = bs.get_winner(log[-1])
  if winner == 1:
    progress(user)
  return flask.jsonify({'log': log, 'winner': winner})

def get_heroes_of_user(c, user):
  return query(c, 'select rowid as id, * from heroes where user = ?', (user,))

def progress(user):
  c = db()
  c.execute('update users set stage = stage + 1 where email = ?', (user,))

def getdata(c, user):
  progress = query(c, 'select * from users where email = ?', (user,))[0]
  heroes = get_heroes_of_user(c, user)
  return {
    'progress': progress,
    'heroes': heroes,
    'index': Hero.get_index()
  }

@app.route('/getuserdata')
def getuserdata():
  user = flask.request.args['user']
  return flask.jsonify(getdata(db(), user))

@app.route('/searchbeach', methods=['POST'])
def searchbeach():
  user = flask.request.get_json()['user']
  c = db()
  progress = query(c, 'select * from users where email = ?', (user,))[0]
  stage = progress['stage']
  hero_name = random.choice(list(
    name for name, meta in Hero.get_index().items()
    if meta['min_stage'] <= stage))
  hero = {'name': hero_name, 'level': 1}  
  c.execute('update users set day = day + 1 where email = ?', (user,))
  c.execute('insert into heroes values (?, ?, ?)', (hero['name'], hero['level'], user))
  data = getdata(c, user)
  data['just_found'] = hero
  return flask.jsonify(data)

@app.route('/dissolve', methods=['POST'])
def dissolve():
  user = flask.request.get_json()['user']
  rowid = flask.request.get_json()['hero']
  c = db()
  count = query(c, 'select count(1) as cnt from heroes where rowid = ? and user = ?', (rowid, user))[0]['cnt']
  assert(count == 1)
  c.execute('delete from heroes where rowid = ? and user = ?', (rowid, user))
  c.execute('update users set ectoplasm = ectoplasm + 1 where email = ?', (user,))
  return 'OK'

@app.route('/fuse', methods=['POST'])
def fuse():
  user = flask.request.get_json()['user']
  rowid = flask.request.get_json()['hero']
  c = db()
  ectoplasm = query(c, 'select ectoplasm from users where email = ?', (user,))[0]['ectoplasm']
  assert(ectoplasm > 0)
  names = query(c, 'select name from heroes where rowid = ? and user = ?', (rowid, user))
  assert(len(names) == 1)
  name = names[0]['name']
  count = query(c, 'select count(1) as cnt from heroes where name = ? and user = ?', (name, user))[0]['cnt']
  assert(count > 1)
  c.execute('update users set ectoplasm = ectoplasm - 1 where email = ?', (user,))
  c.execute('delete from heroes where rowid != ? and name = ? and user = ?', (rowid, name, user))
  c.execute('update heroes set level = level + 1 where rowid = ?', (rowid,))
  return 'OK'
