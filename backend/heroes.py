from math import sqrt
from collections import defaultdict

class Hero:
  hero_classes = {}

  def __init__(self, level, id, owner, x, y, speed, loyalty_factor, actions):
    self.level = level
    self.id = id
    self.x = x
    self.y = y
    self.speed = speed
    self.loyalty_factor = loyalty_factor
    self.actions = actions
    self.max_loyalty = 8
    self.loyalty = self.max_loyalty * (-1 if owner == 'enemy' else 1)
    self.actions_in_turn = []
    self.status = []
    self.cooldown = defaultdict(int)

  @classmethod
  def __init_subclass__(cls):
    Hero.hero_classes[cls.name] = cls

  @staticmethod
  def create_by_name(name, level, id, owner, x, y):
    return Hero.hero_classes[name](level, id, owner, x, y)

  def speak(self):
    return 'hero'

  def increase_loyalty(self):
    if self.loyalty >= 0:
      self.loyalty += self.loyalty_factor
      self.loyalty = min(5, self.loyalty)
    else:
      self.loyalty -= self.loyalty_factor
      self.loyalty = max(-5, self.loyalty)


  def step(self, stage, state):
    self.actions_in_turn = []
    self.increase_loyalty()
    target = self.find_closest_opponent(state)
    if target is not None:
      attack = self.actions['base_attack']
      distance = sqrt(self.sq_distance(target))
      if distance <= attack['range']:
        if self.cooldown[attack['name']] == 0:
          target.take_attack(attack)
          self.actions_in_turn = [{**attack, 'target_hero': target.id}]
          self.cooldown[attack['name']] = attack['cooldown']
        else:
          self.cooldown[attack['name']] -= 1
      else:
        direction_x, direction_y = self.direction_to_hero(target)
        step_size = min(self.speed, distance + target.speed - attack['range'])
        self.x += direction_x * step_size
        self.y += direction_y * step_size

  def take_attack(self, attack):
    if self.loyalty >= 0:
      self.loyalty -= attack['damage']
    else:
      self.loyalty += attack['damage']

  def get_log_entry(self):
    return {
    'x': self.x,
    'y': self.y,
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

  def __init__(self, level, id, owner, x, y):
    actions = {'base_attack': {'name': 'base_attack', 'range': 3, 'damage': 1, 'cooldown': 7}}
    super().__init__(level, id, owner, x, y, 1, 0.2, actions)

  def speak(self):
    return 'cube'
