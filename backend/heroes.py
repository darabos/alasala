from backend.actions import *

class Hero:
  hero_classes = {}

  def __init__(self, level, id, owner, x, y):
    self.level = level
    self.id = id
    self.x = x
    self.y = y
    self.max_loyalty = 8
    self.loyalty = self.max_loyalty * (-1 if owner == 'enemy' else 1)
    self.actions_in_turn = []
    self.status = []
    self.actions = [a() for a in self.action_classes]

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
        'speed': cls.speed,
        'loyalty_factor': cls.loyalty_factor,
        'weight': cls.weight
      }
      for (name, cls) in Hero.hero_classes.items()}

  def speak(self):
    return 'hero'

  def increase_loyalty(self):
    if self.loyalty >= 0:
      self.loyalty += self.loyalty_factor
      self.loyalty = min(self.max_loyalty, self.loyalty)
    else:
      self.loyalty -= self.loyalty_factor
      self.loyalty = max(-self.max_loyalty, self.loyalty)

  def step(self, stage, state):
    self.actions_in_turn = []
    self.increase_loyalty()
    for action in self.actions:
      if action.usable(self, state):
        action.do()
        self.actions_in_turn.append(action.get_info())
      else:
        action.cooldown_progress = max(0, action.cooldown_progress - 1)
    if not self.actions_in_turn:
      target = self.find_closest_opponent(state)
      if target is not None:
        distance = sqrt(self.sq_distance(target))
        direction_x, direction_y = self.direction_to_hero(target)
        step_size = min(self.speed, distance + target.speed - self.actions[0].range)
        self.x += direction_x * step_size
        self.y += direction_y * step_size

  def take_attack(self, attack):
    if self.loyalty >= 0:
      self.loyalty -= attack.damage
    else:
      self.loyalty += attack.damage

  def get_log_entry(self):
    return {
    'x': self.x,
    'y': self.y,
    'name': self.name,
    'loyalty': self.loyalty,
    'max_loyalty': self.max_loyalty,
    'status': self.status,
    'actions': self.actions_in_turn
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

  def speak(self):
    return 'cube'

class Hark(Hero):
  name = 'Professor Hark'
  title = 'Dean of Arcane Studies',
  speed = 0.5
  loyalty_factor = 0.2
  weight = 8
  action_classes = [BaseAttack]

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

  def speak(self):
    return 'Hark!Hark!'

# class HornedLady(Hero):
#   name = 'Lady Emily'
#
