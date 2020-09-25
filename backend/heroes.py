import backend.shapes as shapes
from backend.actions import *

class Hero:
  hero_classes = {}
  max_loyalty = 8

  def __init__(self, level, id, owner, x, y):
    self.level = level
    self.id = id
    self.x = x
    self.y = y
    self.loyalty = self.max_loyalty * (-1 if owner == 'enemy' else 1)
    self.actions_in_turn = []
    self.status = []
    self.actions = [a(self) for a in self.action_classes]
    self.inspiration = 0

  @classmethod
  def __init_subclass__(cls):
    Hero.hero_classes[cls.name] = cls

  @staticmethod
  def create_by_name(name, level, id, owner, x, y):
    return Hero.hero_classes[name](level, id, owner, x, y)

  @staticmethod
  def get_index():
    return {
      name: {
        'title': cls.title,
        'abilities': cls.abilities,
        'shape': cls.shape,
        'speed': cls.speed,
        'loyalty_factor': cls.loyalty_factor,
        'weight': cls.weight
      }
      for (name, cls) in Hero.hero_classes.items()}

  def increase_loyalty(self):
    if self.loyalty >= 0:
      self.loyalty += self.loyalty_factor
      self.loyalty = min(self.max_loyalty, self.loyalty)
    else:
      self.loyalty -= self.loyalty_factor
      self.loyalty = max(-self.max_loyalty, self.loyalty)

  def before_step(self):
    pass

  def after_step(self):
    pass
  
  def step(self, state, step_number):
    self.before_step()

    if (step_number % 10) == 0:
      self.inspiration += 1

    self.actions_in_turn = []
    self.increase_loyalty()
    cool_actions = [a for a in self.actions if a.is_cool()]
    for action in cool_actions:
      action.prepare(state)
    cool_actions.sort(reverse=True, key=lambda a: a.hankering())
    resources = {
      'attention': 1,
      'inspiration': self.inspiration
    }
    for action in cool_actions:
      if action.hankering() <= 0:
        break
      if action.resources_sufficient(resources):
        action.consume_resources(resources)
        action.do()
        self.actions_in_turn.append(action.get_info())

    self.inspiration = resources['inspiration']
        
    for action in self.actions:
      action.cool()

    if resources['attention']:
      self.move(state)

    self.after_step()

  def move(self, state):
    target = self.find_closest_opponent(state)
    min_range = min(a.range for a in self.actions)
    if target is not None:
      distance = sqrt(self.sq_distance(target))
      direction_x, direction_y = self.direction_to_hero(target)
      step_size = max(
        0, min(self.speed, distance, distance + target.speed - min_range))
      self.x += direction_x * step_size
      self.y += direction_y * step_size


  def get_log_entry(self):
    return {
    'x': self.x,
    'y': self.y,
    'name': self.name,
    'loyalty': self.loyalty,
    'max_loyalty': self.max_loyalty,
    'status': self.status,
    'actions': self.actions_in_turn,
    'inspiration': self.inspiration
    }

  def direction_to_hero(self, other):
    x = other.x - self.x
    y = other.y - self.y
    length = sqrt(x ** 2 + y ** 2)
    return x/length, y/length

  def teammate(self, other):
    return (self.loyalty < 0 and other.loyalty < 0) or (self.loyalty >= 0 and other.loyalty >=0)

  def sq_distance(self, other):
    return (other.x - self.x)**2 + (other.y - self.y)**2

  def find_closest_opponent(self, state):
    opponents = list(filter(lambda h: not self.teammate(h), state))
    if opponents:
      return min(opponents, key=lambda h: self.sq_distance(h))
    else:
      return None

class Cube(Hero):
  name = 'cube'
  title = 'Platonic Solid'
  speed = 1
  weight = 1
  loyalty_factor = 0.1
  abilities = []
  action_classes = [BaseAttack]
  shape = shapes.cube

class Hark(Hero):
  name = 'Professor Hark'
  title = 'Dean of Arcane Studies',
  speed = 0.5
  loyalty_factor = 0.2
  weight = 8
  action_classes = [BrutalAttack]
  shape = shapes.bull

  # Eventually these would become classes, but for now, it's just for display.
  abilities = [
    {
      'name': 'Bookstorm',
      'description':
      'Hark throws 5 books at opponents ahead of him.  Unlocked at level 1.',
      'unlockLevel': 1,
    },
    {
      'name': 'Scientific Method',
      'description':
      'Hark damages everyone around him 5 times and observes the results.  Unlocked at level 5.',
      'unlockLevel': 5,
    },
    {
      'name': 'Reading Glasses',
      'description': 'Passive. Hark never misses. Unlocked at level 10.',
      'unlockLevel': 10,
    }
  ]


class Healer(Hero):
  name = 'healer'
  title = 'Angelic Presence'
  speed = 0
  weight = 1
  loyalty_factor = 0.1
  abilities = []
  action_classes = [FarCaress, HealAll]
  shape = shapes.healer


class Reaper(Hero):
  name = 'Reaper'
  title = 'Diabolic Presence'
  speed = 0.1
  weight = 5
  loyalty_factor = 0.1
  abilities = []
  action_classes = [Scythe, ComeToPapa]
  shape = shapes.krokotyuk

