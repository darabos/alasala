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
      create table users (email text, stage int, day int)
      insert into users values ("test", 0, 1)
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

@app.route('/computecombat')
def computecombat():
  user = flask.request.args['user']
  party = list(map(int, flask.request.args['party'].split(',')))
  stage = flask.request.args['stage']
  c = db()
  heroes = get_heroes_of_user(c, user)

  def find_hero_by_id(id):
    for h in heroes:
      if h['id'] == id:
        return h

  heroes_in_party = [find_hero_by_id(hero_id) for hero_id in party]
  log = bs.simulate_battle(heroes_in_party, stage)
  return flask.jsonify(log)

def get_heroes_of_user(c, user):
  return query(c, 'select rowid as id, * from heroes where user = ?', (user,))


@app.route('/getuserdata')
def getuserdata():
  user = flask.request.args['user']
  c = db()
  progress = query(c, 'select * from users where email = ?', (user,))[0]
  heroes = get_heroes_of_user(c, user)
  return flask.jsonify({
    'progress': progress,
    'heroes': heroes,
    'index': Hero.get_index()
  })

@app.route('/searchbeach', methods=['POST'])
def searchbeach():
  user = flask.request.get_json()['user']
  hero = random.choice([
    {'name': 'cube', 'level': 1},
    {'name': 'Professor Hark', 'level': 1}])
                       
  c = db()
  c.execute('update users set day = day + 1 where email = ?', (user,))
  c.execute('insert into heroes values (?, ?, ?)', (hero['name'], hero['level'], user))
  progress = query(c, 'select * from users where email = ?', (user,))[0]
  heroes = query(c, 'select rowid as id, * from heroes where user = ?', (user,))
  return flask.jsonify({'progress': progress, 'heroes': heroes, 'just_found': hero})
