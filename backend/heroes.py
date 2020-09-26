import math
import random
import backend.shapes as shapes
from copy import deepcopy
from backend.actions import *

class Hero:
  hero_classes = {}
  story = []
  max_loyalty_base = 7
  max_loyalty_per_level = 3
  speed_base = 1
  speed_per_level = 0
  influence_base = 1
  influence_per_level = 0.3
  # This hero can only be found on the beach after this stage.
  min_stage = 0
  num_conversations = 0
  is_chewbacca = False

  def __init__(self, level, id, owner, x, y):
    self.level = level

    self.max_loyalty = (
      self.max_loyalty_base + level * self.max_loyalty_per_level)
    self.speed = self.speed_base + level * self.speed_per_level
    self.influence = self.influence_base + level * self.influence_per_level

    self.id = id
    self.x = x
    self.y = y
    self.start_x = x
    self.start_y = y
    self.loyalty = self.max_loyalty * (-1 if owner == 'enemy' else 1)
    self.actions_in_turn = []
    self.status = []
    self.actions = [
      a(self) for a in self.action_classes if self.level >= a.min_level]
    self.inspiration = 0
    self.init()

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
        'name': cls.name,
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
        'min_stage': cls.min_stage,
      }
      for (name, cls) in Hero.hero_classes.items()}

  def has_status(self, stype):
    return any(s['type'] == stype for s in self.status)

  def remove_status(self, stype):
    self.status = [s for s in self.status if s['type'] != stype]

  def add_status(self, stype, **kwargs):
    self.status.append({'type': stype, **kwargs})

  def is_frozen(self):
    return self.num_conversations != 0

  def hit(self, amount, by=None):
    self.remove_status('Concentrating') # Concentrating spells are interrupted by hits.
    if self.has_status('Thoughtworm'): amount *= 1.5
    self.switched = abs(amount) > abs(self.loyalty) # Only valid in hit() overrides.

    # Core logic.
    amount = math.copysign(amount, self.loyalty)
    self.loyalty -= amount

    for s in self.status[:]:
      if s['type'] == 'Safety Collar' and self.switched:
        self.status.remove(s)
        self.hit(s['damage'])
      if s['type'] == 'Thoughtworm' and self.switched:
        self.status.remove(s)
      if s['type'] == 'Anaesthesia' and self.switched:
        self.status.remove(s)
      if s['type'] == 'Infectious' and by:
        by.add_status('Thoughtworm', damage=s['damage'])
        self.status.remove(s)

  def heal(self, amount):
    amount = math.copysign(amount, self.loyalty)
    self.loyalty += amount
    if self.loyalty > self.max_loyalty:
      self.loyalty = self.max_loyalty

  def before_step(self, state):
    pass

  def after_step(self, state):
    pass

  def init(self):
    pass

  def step(self, state, step_number):
    self.actions_in_turn = []
    if self.is_frozen():
      return

    self.before_step(state)

    self.apply_status_effects(state)

    if self.has_status('Anaesthesia'):
      if random.random() + self.influence / 20 >= 0.1:
        self.remove_status('Anaesthesia')
      return

    cool_actions = [a for a in self.actions if a.is_cool()]
    for action in cool_actions:
      action.prepare(state)
    cool_actions.sort(reverse=True, key=lambda a: a.hankering())

    resources = {
      'attention': 1,
      'inspiration': self.inspiration
    }
    self.inspiration = 0

    for action in cool_actions:
      if action.hankering() <= 0:
        break
      if action.resources_sufficient(resources):
        action.consume_resources(resources)
        action.do()
        self.actions_in_turn.append(action.get_info())

    self.inspiration = min(3, self.inspiration + resources['inspiration'])

    for action in self.actions:
      action.cool()

    if resources['attention']:
      self.move(state)

    self.after_step(state)

  def apply_status_effects(self, state):
    for s in self.status[:]:
      if s['type'] == 'Mushroom':
        for h in self.allies_within(state, 10):
          h.hit(s['damage'])
      if 'duration' in s:
        s['duration'] -= 1
        if s['duration'] <= 0:
          self.status.remove(s)
      if s['type'] == 'Thoughtworm':
        self.hit(s['damage'])

  def move(self, state):
    target = self.find_closest_opponent(state)
    min_range = min(a.range for a in self.actions)
    if target is not None:
      distance = sqrt(self.sq_distance(target))
      step_size = max(
        0, min(self.speed, distance, distance + target.speed - min_range))
      if step_size > 0:
        direction_x, direction_y = self.direction_to_hero(target)
        self.x += direction_x * step_size
        self.y += direction_y * step_size


  def get_log_entry(self):
    return deepcopy({
    'x': self.x,
    'y': self.y,
    'name': self.name,
    'loyalty': self.loyalty,
    'max_loyalty': self.max_loyalty,
    'status': self.status,
    'actions': self.actions_in_turn,
    'inspiration': self.inspiration,
    })

  def direction_to_hero(self, other):
    x = other.x - self.x
    y = other.y - self.y
    length = sqrt(x ** 2 + y ** 2)
    return (x/length, y/length) if length else (0, 0)

  def teammate(self, other):
    return (self.loyalty < 0 and other.loyalty < 0) or (self.loyalty >= 0 and other.loyalty >=0)

  def sq_distance(self, other):
    return (other.x - self.x)**2 + (other.y - self.y)**2

  def opponents_within(self, state, radius):
    for h in state:
      if not self.teammate(h) and self.sq_distance(h) <= radius * radius:
        yield h

  def allies_within(self, state, radius):
    for h in state:
      if h is not self and self.teammate(h) and self.sq_distance(h) <= radius * radius:
        yield h

  def find_closest_opponent(self, state):
    opponents = list(filter(lambda h: not self.teammate(h), state))
    if opponents:
      chewbaccas = list(filter(lambda o: o.is_chewbacca, opponents))
      if chewbaccas:
        return chewbaccas[0]
      else:
        return min(opponents, key=lambda h: self.sq_distance(h))
    else:
      return None

  def find_closest_ally(self, state):
    opponents = list(filter(lambda h: h is not self and self.teammate(h), state))
    if opponents:
      return min(opponents, key=lambda h: self.sq_distance(h))
    else:
      return None

class Cube(Hero):
  min_stage = 1000 # Used in development.
  name = 'cube'
  title = 'Platonic Solid'
  abilities = []
  action_classes = [BaseAttack]
  shape = shapes.cube

class Hark(Hero):
  min_stage = 1000 # Used in development.
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
  min_stage = 1000 # Used in development.
  name = 'healer'
  title = 'Angelic Presence'
  speed_base = 0
  abilities = []
  action_classes = [FarCaress, HealAll]
  shape = shapes.bear


class Chicken(Hero):
  name = 'Amangelica'
  title = 'Graduate Student in Biology'
  speed_base = 1
  abilities = [
    { 'name': 'Edible wildlife',
      'description': 'Amangelica often finds small bugs or roots that allow her to regain some health. And have interesting flavors.',
      'unlockLevel': 1 },
    { 'name': 'Inspiring Conversion',
      'description': 'Amangelica gains 1 inspiration each time she is converted.',
      'unlockLevel': 2 },
    { 'name': 'Safety Collar',
      'description': 'Amangelica puts a nice collar on the closest ally. The collar will stab the ally if they convert, hopefully converting them back. Takes 3 inspiration.',
      'unlockLevel': 2 },
    { 'name': 'Spontaneous Inspiration',
      'description': 'Amangelica gains inspiration at random times. Sometimes while brushing her beak!',
      'unlockLevel': 3 },
    ]
  action_classes = [BaseAttack, EdibleWildlife, SafetyCollar]
  shape = shapes.chicken
  def before_step(self, state):
    # Spontaneous Inspiration
    if self.level >= 3 and random.random() < 0.01 * self.level and self.inspiration < 3:
      self.inspiration += 1

  def hit(self, amount, by=None):
    super().hit(amount, by)
    if self.level >= 2 and self.switched and self.inspiration < 3:
      self.inspiration += 1


class Wizard(Hero):
  name = 'Gumdorfin'
  title = 'Alchemist of the Second Order'
  speed_base = 1
  abilities = [
    { 'name': 'Superior Organism',
      'description': 'Gumdorfin casts a spell to transform an enemy into a mushroom. Mushrooms continuously damage their nearby allies.',
      'unlockLevel': 2 },
    { 'name': 'Astral Boar',
      'description': 'Gumdorfin summons an invisible boar that eats all mushrooms. Takes 3 inspiration.',
      'unlockLevel': 3 },
    { 'name': 'Aggressive Inspiration',
      'description': 'Gumdorfin often gains inspiration when attacking someone.',
      'unlockLevel': 1 },
    ]
  action_classes = [InspiringAttack, SuperiorOrganism, AstralBear]
  shape = shapes.wizard


class InfectedSailor(Hero):
  max_loyalty_base = 10
  max_loyalty_per_level = 3
  name = 'Jonathon'
  title = 'Bearlike Infected Sailor'
  speed_base = 1
  abilities = [
    { 'name': 'Asymptomatic Carrier',
      'description': 'Jonathon has gotten used to the effects of the Thoughtworm and now operates normally while carrying one.',
      'unlockLevel': 1 },
    { 'name': 'Infectious Touch',
      'description': 'Jonathon starts the fight with a Thoughtworm in his belly. The first enemy to hit him takes on this worm. The affected enemy loses loyalty over time and is 50% more susceptible to attacks. The Thoughtworm matures and flies off as a Thoughtbutterfly when the enemy is converted.',
      'unlockLevel': 2 },
    { 'name': 'Aggressive Inspiration',
      'description': 'Jonathon often gains inspiration when attacking someone.',
      'unlockLevel': 1 },
    { 'name': 'An Egg Hatches',
      'description': 'When Jonathon has collected 3 Inspiration, a new Thoughtworm hatches is his belly. (Unless there is already one.)',
      'unlockLevel': 3 },
    ]
  action_classes = [InspiringAttack, AnEggHatches]
  shape = shapes.bear
  def init(self):
    if self.level >= 2:
      self.add_status('Infectious', damage=self.influence * 0.1)

class BullLady(Hero):
  max_loyalty_base = 14
  max_loyalty_per_level = 4
  influence_base = 1.4
  influence_per_level = 0.4
  name = 'Megenona'
  title = 'Bull Lady of the South'
  speed_base = 1.1
  abilities = [
    { 'name': 'Painful Inspiration',
      'description': 'Megenona often gains inspiration when hit.',
      'unlockLevel': 1 },
    { 'name': 'Violent Presence',
      'description': 'Megenona exudes an aura of demoralization that continuously damages the loyalty of nearby enemies.',
      'unlockLevel': 2 },
    { 'name': 'In Medias Res',
      'description': 'Megenona leaps into the air and grabs a foe with her whip. They land in each others\' starting places.',
      'unlockLevel': 3 },
    { 'name': 'Escalating Violence',
      'description': 'When Megenona has collected 3 Inspiration she spends it to power up her Violent Presence.',
      'unlockLevel': 4 },
    ]
  action_classes = [BaseAttack, InMediasRes, EscalatingViolence]
  shape = shapes.bull
  def hit(self, amount, by=None):
    super().hit(amount, by)
    # Painful Inspiration
    if self.inspiration < 3 and random.random() < 0.05 * self.level:
      self.inspiration += 1
  def init(self):
    self.violence = 1
  def before_step(self, state):
    # Violent Presence
    if self.level >= 2:
      for h in self.opponents_within(state, 10):
        h.hit(self.violence * 0.1 * self.influence)

class Knight(Hero):
  max_loyalty_base = 6
  max_loyalty_per_level = 3
  influence_base = 1.2
  influence_per_level = 0.2
  name = 'Humbalot'
  title = 'Member of the Holy Mackerels'
  speed_base = 0.9
  abilities = [
    { 'name': 'Painful Inspiration',
      'description': 'Humbalot often gains inspiration when hit.',
      'unlockLevel': 1 },
    { 'name': 'Reflective Armor',
      'description': 'Humbalot is heavily armored. The armor reflects 10% of attacks per level.',
      'unlockLevel': 2 },
    { 'name': 'Exude Conviction',
      'description': 'Humbalot can shout his conviction loudly for everyone around to hear. This erodes the loyalty of opponents nearby. Costs 3 Inspiration.',
      'unlockLevel': 3 },
    ]
  action_classes = [BaseAttack, ExudeConviction]
  shape = shapes.knight
  def hit(self, amount, by=None):
    # Painful Inspiration
    if self.inspiration < 3 and random.random() < 0.05 * self.level:
      self.inspiration += 1
    # Reflective Armor
    if self.level >= 2 and random.random() < 0.1 * self.level and by:
      by.hit(amount, self)
    else:
      super().hit(amount, by)

class CursePrincess(Hero):
  max_loyalty_base = 6
  max_loyalty_per_level = 3
  influence_base = 1.2
  influence_per_level = 0.2
  name = 'Ykta Laq'
  title = 'Princess of Wild Milk'
  speed_base = 0.9
  abilities = [
    { 'name': 'Aggressive Inspiration',
      'description': 'Ykta Laq often gains inspiration when attacking someone.',
      'unlockLevel': 1 },
    { 'name': 'Unpredictable Journey',
      'description': 'Ykta Laq moves around on the battlefield and opponents have a hard time tracking her.',
      'unlockLevel': 2 },
    { 'name': 'Curse Flight',
      'description': 'Ykta Laq is a curse in a human body. For 3 Inspiration she can leave her mortal form and move as a curse for a short while. In this form she cannot be harmed, regenerates loyalty, and harms the loyalty of opponents that she touches.',
      'unlockLevel': 4 },
    ]
  action_classes = [InspiringRangedAttack, UnpredictableJourney, CurseFlight]
  shape = shapes.knight
  def hit(self, amount, by=None):
    if not self.has_status('Curse Flight'):
      super().hit(amount, by)
  def before_step(self, state):
    # Violent Presence
    if self.has_status('Curse Flight'):
      self.heal(0.5 * self.influence)
      for h in self.opponents_within(state, 1):
        h.hit(0.5 * self.influence)


class Reaper(Hero):
  name = 'Reaper'
  title = 'Diabolic Presence'
  min_stage = 3
  speed_base = 0.1
  abilities = []
  action_classes = [Scythe, ComeToPapa, InspiredByTime]
  shape = shapes.reaper

class CrocodileMan(Hero):
  name = 'CrocodileMan'
  title = 'Smelly Reptile'
  abilities = []
  action_classes = [FlipWeakest, PushBackAttack]
  shape = shapes.krokotyuk
  anger = 0
  def hit(self, amount, by=None):
    super().hit(amount, by)
    self.anger += amount
    normal_influence = self.influence_base + self.level * self.influence_per_level
    self.influence = normal_influence * (self.anger / self.max_loyalty + 1)

class Monkey(Hero):
  name = 'Crazy Monkey'
  title = 'Itchy Fleabag'
  abilities = []
  action_classes = [Scratch]
  speed_base = 2
  speed_per_level = 0.5
  shape = shapes.monkey

  def before_step(self, state):
    if hasattr(self, 'prev_loyalty'):
      if ((abs(self.prev_loyalty) > abs(self.loyalty)) or
          (self.prev_loyalty * self.loyalty < 0)):
        if random.random() < 0.6:
          self.loyalty = self.prev_loyalty
    self.prev_loyalty = self.loyalty

  def move(self, state):
    if not hasattr(self,'target'):
      self.target = None
    if not self.target:
      enemies = [hero for hero in state if not self.teammate(hero)]
      if enemies:
        self.target = random.choice(enemies)
    if self.target:
      distance = sqrt(self.sq_distance(self.target))
      if distance < 1:
        self.target = None # Maybe next round...
      else:
        direction_x, direction_y = self.direction_to_hero(self.target)
        step_size = max(
          0, min(self.speed, distance + self.target.speed - 1))
        self.x += direction_x * step_size
        self.y += direction_y * step_size

class Scientist(Hero):
  name = 'Derek'
  title = 'Head of Thoughtworm Research'
  shape = shapes.scientist
  in_conversation_with = None
  influence_per_level = 0.2

  abilities = [
    {
      'name': 'Teacher',
      'description':
      '''Derek gains inspiration from teaching. Every time he attacks a different
opponent, his inspiration increases.''',
      'unlockLevel': 1,
    },
    {
      'name': "Aumann's agreement theorem",
      'description':
      '''When Derek gains enough inspiration, he starts an engaging conversation
      with an opponent. They are both unable to move or act and lose health at
      an increasing rate until one of them is converted.
''',
      'unlockLevel': 1,
    }

    ]
  action_classes = [DiversityAttack, EngageInConversation]

class ThoughtWorm(Hero):
  name = 'ThoughtWorm'
  title = 'Predator of Memes'
  shape = shapes.snake
  influence_per_level = 0.2

  abilities = []

  action_classes = [ChannelingAttack, Anaesthetise, InspiredByTime]

class RescueParrot(Hero):
  name = 'Rescue Parrot'
  title = 'Avian Missionary'
  shape = shapes.giantparrot

  def hit(self, amount, by=None):
    super().hit(amount, by)
    # Painful Inspiration
    if self.inspiration < 3 and random.random() < 0.6 * self.level:
      self.inspiration += 1

  abilities = []

  action_classes = [Rescue, EnemyRescue, LookingForTrouble]

class Politician(Hero):
  name = 'Will'
  title = 'Aspiring Politician'
  shape = shapes.politician
  chewbacca_reflected = 0
  action_classes = [RandomInspiringAttack, ChewbaccaDefense]

  @property
  def max_chewbacca_reflected(self):
    return 2.5 * self.influence

  abilities = [
    {
      'name': 'Chewbacca defense',
      'description': '''The Chewbacca defense is so infuriating to listen to
      that all enemies are forced to attack Will while he is speaking, but Will
      just reflects the damage back to the attacker.''',
      'unlockLevel': 1
    },
    {
      'name': 'Power of convincing',
      'description': '''Gains inspiration from attacking others.''',
      'unlockLevel' : 1
    }
  ]

  def hit(self, amount, by=None):
    effective_amount = amount
    if self.is_chewbacca and by is not None:
      reflected = min(self.max_chewbacca_reflected - self.chewbacca_reflected, amount)
      self.chewbacca_reflected += reflected
      if self.chewbacca_reflected >= self.max_chewbacca_reflected:
        self.is_chewbacca = False
        self.chewbacca_reflected = 0
      effective_amount = amount - reflected
      by.hit(reflected, self)
    super().hit(effective_amount, by)
