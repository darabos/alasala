from backend.heroes import Hero


def get_player_state(heroes):
  print(heroes)
  return [Hero.create_by_name(
  name=hero['name'],
  level=hero['level'],
  id=hero['id'],
  owner='player',
  x=0.5 * (i + 1),
  y=0.5 * (i + 1)) for (i, hero) in enumerate(heroes)]


def get_enemy_state(stage):
  return [Hero.create_by_name(
  name='cube',
  level=1,
  id=-(i + 1),
  owner='enemy',
  x= 10 - 0.5 * (i + 1),
  y= 0.5 * (i + 1)) for i in range(5)]


def battle_is_over(turn):
  first = True
  for _, log_entry in turn.items():
    if first:
      loyal_to_player = log_entry['loyalty'] >= 0
      first = False
    elif loyal_to_player != (log_entry['loyalty'] >= 0):
      return False
  return True


def simulate_battle(heroes, stage):
  state = get_player_state(heroes) + get_enemy_state(stage)
  turns = [{hero.id: hero.get_log_entry() for hero in state}]
  while not battle_is_over(turns[-1]) and len(turns) < 5 * 90:
    for hero in state:
      hero.step(stage, state)
    turns.append({hero.id: hero.get_log_entry() for hero in state})
  return turns
