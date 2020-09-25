import math
import random
import backend.shapes as shapes
from backend.actions import *

def sign(x):
  return math.copysign(1, x)


class Hero:
  hero_classes = {}
  story = []
  max_loyalty_base = 7
  max_loyalty_per_level = 1
  speed_base = 1
  speed_per_level = 0
  influence_base = 1
  influence_per_level = 0
  # This hero can only be found on the beach after this stage.
  min_stage = 0

  def __init__(self, level, id, owner, x, y):
    self.level = level

    self.max_loyalty = (
      self.max_loyalty_base + level * self.max_loyalty_per_level)
    self.speed = self.speed_base + level * self.speed_per_level
    self.influence = self.influence_base + level * self.influence_per_level
    
    self.id = id
    self.x = x
    self.y = y
    self.loyalty = self.max_loyalty * (-1 if owner == 'enemy' else 1)
    self.actions_in_turn = []
    self.status = []
    self.actions = [
      a(self) for a in self.action_classes if self.level >= a.min_level]
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
        'story': cls.story,
        'shape': cls.shape,
        'max_loyalty_base': cls.max_loyalty_base,
        'max_loyalty_per_level': cls.max_loyalty_per_level,
        'speed_base': cls.speed_base,
        'speed_per_level': cls.speed_per_level,
        'influence_base': cls.influence_base,
        'influence_per_level': cls.influence_per_level,
        'weight': shapes.weightOf(cls.shape),
        'min_stage': cls.min_stage
      }
      for (name, cls) in Hero.hero_classes.items()}

  def hit(self, amount):
    amount = math.copysign(amount, self.loyalty)
    switched = abs(amount) > abs(self.loyalty)
    self.loyalty -= amount
    for s in self.status[:]:
      if s['type'] == 'SafetyCollar' and switched:
        self.status.remove(s)
        self.hit(s['damage'])

  def heal(self, amount):
    amount = math.copysign(dmg, self.loyalty)
    self.loyalty += amount

  def before_step(self):
    pass

  def after_step(self):
    pass
  
  def step(self, state, step_number):
    self.before_step()

    self.actions_in_turn = []
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
  abilities = []
  action_classes = [BaseAttack]
  shape = shapes.cube

class Hark(Hero):
  name = 'Professor Hark'
  title = 'Dean of Arcane Studies',
  speed_base = 0.5
  influence_per_level = 0.2
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
  story = [
      dict(voice='hark1.m4a', text='''I have studied the ancient legends about the island of Alasala. They say it is cursed.
  The only way to reach it is by a shipwreck. The curse engulfs the castaways and keeps them on the island,
  forever. This brings us to our question...'''),
      dict(voice='hark2.m4a', text='''Namely, how shall we capture this curse? How will we transport it back to England to study in my laboratory?'''),
      dict(voice='hark3.m4a', text='''Do you have an imaginative mind? Can you fathom the knowledge we could extract from such an experiment?'''),
      dict(voice='hark4.m4a', text='''We must learn more. No matter the cost. I will lead this group to the heart of Alasala and do what I must.'''),
  ]


class Healer(Hero):
  name = 'healer'
  title = 'Angelic Presence'
  speed_base = 0
  abilities = []
  action_classes = [FarCaress, HealAll]
  shape = shapes.healer


class Reaper(Hero):
  name = 'Reaper'
  title = 'Diabolic Presence'
  min_stage = 3
  speed_base = 0.1
  abilities = []
  action_classes = [Scythe, ComeToPapa]
  shape = shapes.reaper

class CrocodileMan(Hero):
  name = 'CrocodileMan'
  title = 'Smelly Reptile'
  abilities = []
  action_classes = [FlipWeakest, PushBackAttack]
  shape = shapes.krokotyuk
  anger = 0
  def hit(self, amount):
    super().hit(amount)
    self.anger += amount
    normal_influence = self.influence_base + self.level * self.influence_per_level
    self.influence = normal_influence * (self.anger / self.max_loyalty + 1)
