from math import sqrt, copysign

class Action:
  # How much cooldown it needs.
  cooldown = 0

  # Leave unchanged for actions where affect has unlimited range.
  range = 99999

  # It uses up this much inspiration.
  inspiration = 0

  # It uses up this much attention. Attention is reset to 1 at the
  # start of each round. This is basically a mechanism to restrict
  # heros to do only one of certain attention-requiring actions.
  # Attention is also used for walking.
  attention = 1

  # Used by the UI to decide what animation to show when this action
  # is found in the journal.
  animation_name = "Override me you dummy!"

  # Heros can only use this above the below level.
  min_level = 1

  def __init__(self, subject):
    self.subject = subject
    self.cooldown_progress = 0
    self.resource_needs = {
      'attention': self.attention,
      'inspiration': self.inspiration
    }

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

  def resources_sufficient(self, resources):
    for (resource, need) in self.resource_needs.items():
      if resources[resource] < need:
        return False
    return True

  def consume_resources(self, resources):
    for (resource, need) in self.resource_needs.items():
      resources[resource] -= need

  # Do what you have to do...
  def apply_effect(self):
    pass

  def do(self):
    self.apply_effect()
    self.cooldown_progress = self.cooldown

  def get_info(self):
    return {'animation_name': self.animation_name}


class SimpleAttack(Action):
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
    self.target.loyalty += copysign(
      self.damage * self.subject.influence,
      self.subject.loyalty)

  def get_info(self):
    return {**super().get_info(),
            'range': self.range,
            'damage': self.damage,
            'target_hero': self.target.id}


class BaseAttack(SimpleAttack):
  range = 3
  damage = 1
  cooldown = 7

class BrutalAttack(SimpleAttack):
  range = 10
  damage = 3
  cooldown = 10

class FarCaress(SimpleAttack):
  range = 7
  damage = 0.1
  cooldown = 1

class Scythe(SimpleAttack):
  range = 1.5
  damage = 8
  cooldown = 10
  min_level = 2

class Scratch(SimpleAttack):
  attention = 0
  range = 2
  damage = 0.3
  cooldown = 3


class PushBackAttack(SimpleAttack):
  range = 3
  damage = 1
  cooldown = 7
  push_back = 2

  def apply_effect(self):
    super().apply_effect()
    direction_x, direction_y = self.subject.direction_to_hero(self.target)
    self.target.x += direction_x * self.push_back
    self.target.y += direction_y * self.push_back

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
  inspiration = 1

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

class FlipWeekest(Action):
  default_hankering = 10
  cooldown = 10
  inspiration = 1

  def prepare(self, state):
    enemies = [hero for hero in state if not self.subject.teammate(hero)]
    self.target = None
    if enemies:
      self.target = min(enemies, key = lambda h: abs(h.loyalty))

  def apply_effect(self):
    self.target.loyalty = -self.target.loyalty

  def get_info(self):
    return {**super().get_info(),
            'target_hero': self.target}

class MemorableAttack(BaseAttack):
  last_target = None
  def apply_effect(self):
    super().apply_effect()
    if self.target != self.last_target:
      self.inspiration += 1
    self.last_target = self.target

class StartConversation(SimpleAttack):
  default_hankering = 10
  inspiration = 1
  cooldown = 10
  range = 3

  animation_name = 'start_conversation'

  def is_cool(self):
    if self.subject.in_conversation_with is not None:
      return False
    else:
      return super().is_cool()

  def apply_effect(self):
    print('starting_conversation!')
    self.subject.in_conversation_with = self.target
    self.target.num_conversations += 1
    self.subject.num_conversations += 1


class ContinueConversation(SimpleAttack):
  default_hankering = 10
  damage = 0
  over = False
  animation_name = 'mutual_simple_attack'

  def is_cool(self):
    return self.subject.in_conversation_with is not None

  def prepare(self, stage):
    self.target = self.subject.in_conversation_with

  def apply_effect(self):
    print('ContinueConversation')
    self.damage += 0.5
    for hero in [self.target, self.subject]:
      prev_loyalty_sign = copysign(1, hero.loyalty)
      hero.loyalty += copysign(self.damage * self.subject.influence, hero.loyalty)
      current_loyalty_sign = copysign(1, hero.loyalty)
      if prev_loyalty_sign != current_loyalty_sign:
        self.over = True
    if self.over:
      self.back_to_init()

  def back_to_init(self):
    self.damage = 0
    self.over = False
    self.target.num_conversations -= 1
    self.subject.num_conversations -= 1
    self.subject.in_conversation_with = None
