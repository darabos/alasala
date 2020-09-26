from math import sqrt, copysign
import random
import re

def sign(x):
  return copysign(1, x)

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

  # Used by the UI to decide what animation or text to show when this action
  # is found in the journal.
  animation_name = ''

  # Heros can only use this above the below level.
  min_level = 1

  default_hankering = 1

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
    return self.default_hankering

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
    if not self.animation_name:
      classname = type(self).__name__
      parts = re.findall('[A-Z][a-z]*', classname)
      self.animation_name  = ' '.join(parts)
    # Changing spaces to non-breaking spaces.
    return {'animation_name': self.animation_name.replace(' ', ' ')}


class ConcentratingAction(Action):
  concentrating_turns = 3
  concentrating = False
  attention = 1
  def apply_effect(self):
    if self.concentrating:
      if not self.subject.has_status('Concentrating'): # Interrupted.
        self.concentrating = False
        self.cooldown = self.saved_cooldown
        self.inspiration = self.saved_inspiration
        return
      self.concentrating += 1
      if self.concentrating == self.concentrating_turns:
        self.subject.remove_status('Concentrating')
        self.concentrating = False
        self.cooldown = self.saved_cooldown
        self.inspiration = self.saved_inspiration
        self.final_effect()
    else:
      self.saved_cooldown = self.cooldown
      self.cooldown = 0
      self.saved_inspiration = self.inspiration
      self.inspiration = 0
      self.concentrating = 1
      self.subject.add_status('Concentrating')
  def hankering(self):
    return 99


class SimpleAttack(Action):
  damage = None
  default_hankering = 1
  animation_name = 'Attack'

  def prepare(self, state):
    self.target = self.subject.find_closest_opponent(state)

  def hankering(self):
    if self.target and (sqrt(self.subject.sq_distance(self.target)) <= self.range):
      return self.default_hankering
    return 0

  def apply_effect(self):
    self.target.hit(self.damage * self.subject.influence, self.subject)

  def get_info(self):
    return {**super().get_info(),
            'range': self.range,
            'damage': self.damage,
            'target_hero': self.target.id}


class BaseAttack(SimpleAttack):
  range = 3
  damage = 1
  cooldown = 7

class InspiringAttack(SimpleAttack):
  range = 3
  damage = 1
  cooldown = 7
  def apply_effect(self):
    super().apply_effect()
    if random.random() < 0.1 * self.subject.level:
      self.subject.inspiration += 1

class InspiringRangedAttack(SimpleAttack):
  range = 12
  damage = 1
  cooldown = 8
  def hankering(self):
    if self.subject.has_status('Curse Flight'):
      return 0
    return super().hankering()
  def apply_effect(self):
    super().apply_effect()
    if random.random() < 0.1 * self.subject.level:
      self.subject.inspiration += 1

class RandomInspiringAttack(SimpleAttack):
  range = 3
  base_damage = 0.8
  cooldown = 7

  def apply_effect(self):
    random_damage = random.random() * 0.2
    self.damage = self.base_damage + random_damage
    if random_damage + 0.05 * self.subject.level > 0.15:
      self.subject.inspiration += 1
    if random_damage + 0.05 * self.subject.level > 0.45:
      self.subject.inspiration += 1
    super().apply_effect()

class BrutalAttack(SimpleAttack):
  range = 10
  damage = 3
  cooldown = 10

class FarCaress(SimpleAttack):
  range = 7
  damage = 0.1
  cooldown = 1

class WizardAttack(SimpleAttack):
  damage = 2.5
  cooldown = 10

class Scythe(SimpleAttack):
  range = 1.5
  damage = 200
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

class ChannelingAttack(Action):
  damage = 1
  default_hankering = 1
  animation_name = 'Channeling'
  cooldown = 8
  range = 5

  def prepare(self, state):
    self.target = self.subject.find_closest_opponent(state)
    self.beneficiary = self.subject.find_closest_ally(state)

  def hankering(self):
    if self.target and self.beneficiary and (sqrt(self.subject.sq_distance(self.target)) <= self.range):
      return self.default_hankering
    return 0

  def apply_effect(self):
    damage = self.damage * self.subject.influence
    self.target.hit(damage, self.subject)
    self.beneficiary.heal(damage)

  def get_info(self):
    return {**super().get_info(),
            'range': self.range,
            'damage': self.damage,
            'target_hero': self.target.id,
            'beneficiary_hero': self.beneficiary.id}

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
      target.heal(self.heal * self.subject.level)

  def get_info(self):
    return {**super().get_info(),
            'heal': self.heal}


class EdibleWildlife(Action):
  def apply_effect(self):
    self.subject.heal(0.1 + self.subject.influence/40)

class SafetyCollar(Action):
  inspiration = 3
  def hankering(self):
    return 4 if self.target else 0
  def prepare(self, state):
    self.target = self.subject.find_closest_ally(state)
  def apply_effect(self):
    if self.target:
      self.target.status.append({'type': 'Safety Collar', 'damage': sqrt(self.subject.influence * 5)})


class SuperiorOrganism(ConcentratingAction):
  cooldown = 10
  def hankering(self):
    return super().hankering() if self.target else 0
  def prepare(self, state):
    self.target = self.subject.find_closest_opponent([h for h in state if not h.has_status('Mushroom')])
  def final_effect(self):
    if self.target and not self.subject.teammate(self.target) and not self.target.has_status('Mushroom'):
      self.target.status.append({'type': 'Mushroom', 'damage': self.subject.influence * 0.2, 'duration': 5 + level // 2})

class AstralBear(Action):
  inspiration = 3
  def hankering(self):
    if self.subject.level < 6: return 0
    return 4 if self.targets else 0
  def prepare(self, state):
    self.targets = [h for h in state if any(s['type'] == 'Mushroom' for s in h.status)]
  def apply_effect(self):
    for t in self.targets:
      t.remove = True

class AnEggHatches(Action):
  inspiration = 3
  def hankering(self):
    if self.subject.level < 3: return 0
    return 0 if self.subject.has_status('Infectious') else 99
  def apply_effect(self):
    self.subject.add_status('Infectious', damage=0.1 * self.subject.influence)

class InMediasRes(Action):
  used = False
  def prepare(self, state):
    t = [h for h in state if h.y == self.subject.y and not self.subject.teammate(h)]
    self.target = t[0] if t else None
  def hankering(self):
    return 99 if self.target and not self.used and self.subject.level >= 3 else 0
  def apply_effect(self):
    self.used = True
    ox = self.subject.x
    self.subject.x = self.target.x
    self.target.x = ox

class EscalatingViolence(Action):
  inspiration = 3
  def hankering(self):
    return 99 if self.subject.level >= 4 else 0
  def apply_effect(self):
    self.subject.violence += 1

class ExudeConviction(Action):
  inspiration = 3
  def prepare(self, state):
    self.targets = list(self.subject.opponents_within(state, 10))
  def hankering(self):
    return 99 if self.targets and self.subject.level >= 3 else 0
  def apply_effect(self):
    for h in self.targets:
      h.hit(3 * self.subject.influence, self)

class UnpredictableJourney(Action):
  cooldown = 27
  def hankering(self):
    return 1
  def apply_effect(self):
    self.subject.x += random.random() * 12 - 6
    self.subject.y += random.random() * 12 - 6

class CurseFlight(Action):
  inspiration = 3
  def hankering(self):
    return 99 if self.subject.level >= 4 else 0
  def apply_effect(self):
    self.subject.add_status('Curse Flight', duration=10)


class ComeToPapa(Action):
  default_hankering = 10
  pull_range = 1
  cooldown = 5
  inspiration = 3

  def prepare(self, state):
    enemies = [hero for hero in state if not self.subject.teammate(hero)]
    self.targets = random.sample(
      enemies, min(len(enemies), self.subject.level + 1))

  def apply_effect(self):
    for target in self.targets:
      direction_x, direction_y = self.subject.direction_to_hero(target)
      target.x = self.subject.x + direction_x * self.pull_range
      target.y = self.subject.y + direction_y * self.pull_range

  def get_info(self):
    return {**super().get_info(),
            'pull_range': self.pull_range}

class FlipWeakest(Action):
  default_hankering = 10
  cooldown = 10
  inspiration = 3
  animation_name = 'Overwhelming Terror'

  def prepare(self, state):
    enemies = [hero for hero in state if not self.subject.teammate(hero)]
    self.target = None
    if enemies:
      self.target = min(enemies, key = lambda h: abs(h.loyalty))

  def apply_effect(self):
    self.target.hit(abs(2 * self.target.loyalty))

  def get_info(self):
    return {**super().get_info(),
            'target_hero': self.target}

class InspiredByTime(Action):
  cooldown = 8
  attention = 0
  animation_name = 'inspired by time'
  def apply_effect(self):
    self.subject.inspiration += 1

  def hankering(self):
    return 1

class DiversityAttack(BaseAttack):
  last_target = None

  def consume_resources(self, resources):
    super().consume_resources(resources)
    if self.target != self.last_target:
      resources['inspiration'] += 1
    self.last_target = self.target


class EngageInConversation(SimpleAttack):
  default_hankering = 99
  inspiration = 1
  orig_cooldown = 10
  cooldown = orig_cooldown
  range = 3
  damage = 0
  in_conversation_with = None
  animation_name = 'Conversation'
  over = False

  def prepare(self, state):
    if self.in_conversation_with is not None:
      self.target = self.in_conversation_with
    else:
      self.target = self.subject.find_closest_opponent(state)

  def apply_effect(self):
    if self.subject.in_conversation_with is None:
      # Start conversation.
      self.subject.in_conversation_with = self.target
      self.target.num_conversations += 1
      self.cooldown = 0
    # Do conversation
    self.damage += 0.5
    talking_heroes = [self.subject.in_conversation_with, self.subject]
    for hittingHero, hitHero in zip(talking_heroes, reversed(talking_heroes)):
      prev_loyalty_sign = sign(hitHero.loyalty)
      hitHero.hit(self.damage * hittingHero.influence)
      current_loyalty_sign = sign(hitHero.loyalty)
      if prev_loyalty_sign != current_loyalty_sign:
        self.over = True
    if self.over:
      self.back_to_init()

  def back_to_init(self):
    self.damage = 0
    self.over = False
    self.target.num_conversations -= 1
    self.subject.in_conversation_with = None
    self.cooldown = self.orig_cooldown

class Anaesthetise(Action):
  default_hankering = 10
  cooldown = 10
  inspiration = 3

  def prepare(self, state):
    enemies = [hero for hero in state if not self.subject.teammate(hero)]
    self.target = None
    if enemies:
      self.target = max(enemies, key = lambda h: abs(h.loyalty))

  def apply_effect(self):
    self.target.add_status('Anaesthesia')

  def get_info(self):
    return {**super().get_info(),
            'target_hero': self.target.id}

class Rescue(Action):
  cooldown = 15

  def hankering(self):
    if self.target:
      return self.default_hankering
    return 0

  def eligible(self, hero):
    return self.subject.teammate(hero) and hero.id != self.subject.id

  def prepare(self, state):
    options = [hero for hero in state if self.eligible(hero)]
    self.target = None
    if options:
      self.target = max(options, key = lambda h: h.max_loyalty - abs(h.loyalty))

  def apply_effect(self):
    if not self.subject.teammate(self.target):
      self.target.hit(abs(2 * self.target.loyalty))

    self.target.x = self.target.start_x
    self.target.y = self.target.start_y
    amount = self.target.max_loyalty - abs(self.target.loyalty)
    self.target.heal(amount)
    self.subject.heal(amount / 2)

  def get_info(self):
    return {**super().get_info(),
            'target_hero': self.target.id}


class EnemyRescue(Rescue):
  inspiration = 3
  default_hankering = 15

  def eligible(self, hero):
    return not self.subject.teammate(hero)

# This never happens. But draws the owner toward enemies.
class LookingForTrouble(Action):
  cooldown = 1000
  range = 1
  def hankering(self):
    return 0

class ChewbaccaDefense(Action):
  default_hankering = 99
  cooldown = 0
  inspiration = 3

  def apply_effect(self):
    self.subject.is_chewbacca = True
