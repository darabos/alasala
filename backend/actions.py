from math import sqrt, copysign

class Action:
  # How much cooldown it needs.
  cooldown = 0
  # It uses up this much inspiration.
  inspiration = 0
  animation_name = "Override me you dummy!"
  # Only one exclusive action is done in a turn
  exclusive = True
  def __init__(self, subject):
    self.subject = subject
    self.cooldown_progress = 0

  def cool(self):
    self.cooldown_progress = max(0, self.cooldown_progress - 1)

  def is_cool(self):
    return self.cooldown_progress == 0

  # Looks at the state. Stores in internal state stuff like
  # whether and who it can target, etc.
  def prepare(self, state):
    pass
    
  # How much the hero wants to do this. =0 if not usable. Cooldown will
  # be handled by hero.
  def hankering(self):
    return 0

  # Do what you have to do...
  def apply_effect(self):
    pass

  def do(self):
    self.apply_effect()
    self.cooldown_progress = self.cooldown

  def get_info(self):
    return {'animation_name': self.animation_name}
  

class SimpleAttack(Action):
  range = None
  damage = None
  default_hankering = 1
  animation_name = 'simple_attack'

  def prepare(self, state):
    self.target = self.subject.find_closest_opponent(state)

  def hankering(self):
    if self.target and (sqrt(self.subject.sq_distance(self.target)) <= self.range):
      return self.default_hankering
    return 0

  def apply_effect(self):
    self.target.loyalty += copysign(self.damage, self.subject.loyalty)

  def get_info(self):
    return {**super().get_info(),
            'range': self.range,
            'damage': self.damage,
            'target_hero': self.target.id}


class BaseAttack(SimpleAttack):
  range=3
  damage=1
  cooldown=7

class BrutalAttack(SimpleAttack):
  range=10
  damage=3
  cooldown=10

class FarCaress(SimpleAttack):
  range=7
  damage=0.1
  cooldown=1

class Scythe(SimpleAttack):
  range=1.5
  damage=8
  cooldown=10

class HealAll(Action):
  default_hankering = 10
  heal = 3
  def prepare(self, state):
    self.targets = [hero for hero in state if self.subject.teammate(hero) and (abs(hero.loyalty) < hero.max_loyalty)]

  def hankering(self):
    if self.targets:
      return self.default_hankering
    return 0

  def apply_effect(self):
    for target in self.targets:
      target.loyalty += copysign(self.heal, self.subject.loyalty)

  def get_info(self):
    return {**super().get_info(),
            'heal': self.heal}


class ComeToPapa(Action):
  default_hankering = 10
  pull_range = 1
  cooldown = 5

  def __init__(self, subject):
    super().__init__(subject)
    self.cooldown_progress = self.cooldown

  def prepare(self, state):
    self.targets = [hero for hero in state if not self.subject.teammate(hero)]

  def hankering(self):
    return self.default_hankering

  def apply_effect(self):
    for target in self.targets:
      direction_x, direction_y = self.subject.direction_to_hero(target)
      target.x = self.subject.x + direction_x * self.pull_range
      target.y = self.subject.y + direction_y * self.pull_range

  def get_info(self):
    return {**super().get_info(),
            'pull_range': self.pull_range}
