from math import sqrt


class Action:
  def __init__(self, name, range, damage, cooldown):
    self.name = name
    self.range = range
    self.damage = damage
    self.cooldown = cooldown
    self.cooldown_progress = 0


  def usable(self, hero, state):
    if hero.actions_in_turn or self.cooldown_progress != 0:
      return False
    else:
      self.target = hero.find_closest_opponent(state)
      if self.target is None:
        return False
      else:
        distance = sqrt(hero.sq_distance(self.target))
        return distance <= self.range


  def do(self):
    self.target.take_attack(self)
    self.cooldown_progress = self.cooldown

  def get_info(self):
    return {'name': self.name,
            'range': self.range,
            'damage': self.damage,
            'target_hero': self.target.id}


class BaseAttack(Action):
  def __init__(self):
    super().__init__('base_attack', range=3, damage=1, cooldown=7)
