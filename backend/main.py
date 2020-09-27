import flask
import flask_cors
import os
import pymysql
import random
import backend.battle_simulator as bs
from backend.heroes import Hero
from backend.stages import stages

from flask_login import LoginManager
from flask_login import login_user, current_user, login_required, logout_user
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized

app = flask.Flask('', static_url_path='/somethingthatwillnevercomeup')
flask_cors.CORS(app, origins='https://alasala-island.web.app', allow_headers='*')

app.secret_key = 'not so top secret'
class AlasalaUser:
  def __init__(self, email):
    self.email = email
  @property
  def is_active(self):
      return True
  @property
  def is_authenticated(self):
      return True
  @property
  def is_anonymous(self):
      return False

  def get_id(self):
      return self.email

  def __str__(self):
      return f'User with email {self.email}'

# ========== Login setup ===========================
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return AlasalaUser(user_id)

secret = open("google_client_secret").read()

google_blueprint = make_google_blueprint(
    client_id=r'965049736612-2b5brso1l4fdkek4qp13640tgrdvkh4u.apps.googleusercontent.com',
    client_secret=secret,
    scope=[
        'openid',
        'https://www.googleapis.com/auth/userinfo.email',
    ]
)
app.register_blueprint(google_blueprint, url_prefix='/auth')

@oauth_authorized.connect
def _on_signin(blueprint, token):
    user_json = google.get('oauth2/v1/userinfo').json()
    us = AlasalaUser(user_json['email'])
    login_user(us)
    
@app.route('/logout')
def logout():
    logout_user()
    return flask.redirect(flask.url_for('indexhtml'))

login_manager.login_view = 'google.login'


def init_table(c, test, commands):
  try:
    test_success = query(c, test)
  except Exception:
    test_success = False
  if not test_success:
    for s in commands.strip().split('\n'):
      print(s)
      c.execute(s)

def db():
  db = getattr(flask.g, '_database', None)
  if db is None:
    db = pymysql.connect(
        user='alasala', password=os.environ['SQL_PASSWORD'],
        unix_socket='/cloudsql/alasala:europe-west1:alasala-pyweek-mysql', db='alasala',
        cursorclass=pymysql.cursors.DictCursor)
    flask.g._database = db
    c = db.cursor()
    init_table(c, 'select * from users where email = "test"', '''
      drop table if exists users
      create table users (email text, stage int, day int, ectoplasm int, rowid mediumint not null auto_increment, primary key (rowid))
      insert into users values ("test", 0, 1, 0, null)
      ''')

    init_table(c, 'select * from heroes where user = "test"', '''
      drop table if exists heroes
      create table heroes (name text, level int, user text, rowid mediumint not null auto_increment, primary key (rowid))
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
  cursor.execute(q, args)
  return cursor.fetchall()

@app.route('/computecombat', methods=['POST'])
@login_required
def computecombat():
  args = flask.request.get_json()
  user = current_user.get_id()
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
  return query(c, 'select *, rowid as id from heroes where user = %s', (user,))

def progress(user):
  c = db()
  c.execute('update users set stage = stage + 1 where email = %s', (user,))

def getdata(c, user):
  res = query(c, 'select * from users where email = %s', (user,))
  if not res:
    c.execute('insert into users values (%s, 0, 1, 0, null)', (user,))
    res = query(c, 'select * from users where email = %s', (user,))
  progress = res[0]
  heroes = get_heroes_of_user(c, user)
  return {
    'progress': progress,
    'heroes': heroes,
    'index': Hero.get_index(),
    'next_stage': stages[progress['stage']],
  }

@app.route('/getuserdata')
@login_required
def getuserdata():
  user = current_user.get_id()
  return flask.jsonify(getdata(db(), user))

@app.route('/searchbeach', methods=['POST'])
@login_required
def searchbeach():
  user = current_user.get_id()
  c = db()
  progress = query(c, 'select * from users where email = %s', (user,))[0]
  stage = progress['stage']
  hero_name = random.choice(list(
    name for name, meta in Hero.get_index().items()
    if meta['min_stage'] <= stage and not meta['npc']))
  hero = {'name': hero_name, 'level': 1}  
  c.execute('update users set day = day + 1 where email = %s', (user,))
  print('insert into heroes values (%s, %s, %s, null)', (hero['name'], hero['level'], user))
  c.execute('insert into heroes values (%s, %s, %s, null)', (hero['name'], hero['level'], user))
  data = getdata(c, user)
  data['just_found'] = hero
  return flask.jsonify(data)

@app.route('/oneofeach', methods=['GET'])
@login_required
def oneofeach():
  user = current_user.get_id()
  c = db()
  for name, meta in Hero.get_index().items():
    hero = {'name': name, 'level': 1}
    c.execute('insert into heroes values (%s, %s, %s, null)', (hero['name'], hero['level'], user))
  return "Your wish was granted"

@app.route('/dissolve', methods=['POST'])
@login_required
def dissolve():
  user = current_user.get_id()
  rowid = flask.request.get_json()['hero']
  c = db()
  count = query(c, 'select count(1) as cnt from heroes where rowid = %s and user = %s', (rowid, user))[0]['cnt']
  assert(count == 1)
  c.execute('delete from heroes where rowid = %s and user = %s', (rowid, user))
  c.execute('update users set ectoplasm = ectoplasm + 1 where email = %s', (user,))
  return 'OK'

@app.route('/fuse', methods=['POST'])
@login_required
def fuse():
  user = current_user.get_id()
  rowid = flask.request.get_json()['hero']
  c = db()
  ectoplasm = query(c, 'select ectoplasm from users where email = %s', (user,))[0]['ectoplasm']
  assert(ectoplasm > 0)
  names = query(c, 'select name from heroes where rowid = %s and user = %s', (rowid, user))
  assert(len(names) == 1)
  name = names[0]['name']
  count = query(c, 'select count(1) as cnt from heroes where name = %s and user = %s', (name, user))[0]['cnt']
  assert(count > 1)
  c.execute('update users set ectoplasm = ectoplasm - 1 where email = %s', (user,))
  to_delete = query(c, 'select rowid from heroes where rowid != %s and name = %s and user = %s limit 1', (rowid, name, user))[0]['rowid']

  c.execute('delete from heroes where rowid = %s and name = %s and user = %s', (to_delete, name, user))
  c.execute('update heroes set level = level + 1 where rowid = %s', (rowid,))
  return 'OK'

@app.route('/')
@login_required
def indexhtml():
    print('this is happening', current_user.get_id())
    return flask.send_from_directory('build', 'index.html')


@app.route('/<path:path>')
@login_required
def static_stuff(path):
    return flask.send_from_directory('build', path)
