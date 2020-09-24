from math import sqrt, copysign

class Action:
  # How much cooldown it needs.
  cooldown = 0
  # It uses up this much inspiration.
  inspiration = 0
  name = "Subclass me you dummy!"
  # Only one exclusive action is done in a turn
  exclusive = True
  def __init__(self, subject):
    self.subject = subject
    self.cooldown_progress = 0
    print('Init', subject, self.name)

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
    return {'name': self.name}
  

class SingleAttack(Action):
  range = None
  damage = None
  default_hankering = 1

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


class BaseAttack(SingleAttack):
  range=3
  damage=1
  cooldown=7
  name = 'base_attack'
