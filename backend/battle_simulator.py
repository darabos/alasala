from backend.heroes import Hero

STARTX = [4, 4, 5, 5, 5]
STARTY = [-0.5, 0.5, -1, 0, 1]
TURNFRAMES = 20
FPS = 60

def get_player_state(heroes):
  print(heroes)
  return [Hero.create_by_name(
  name=hero['name'],
  level=hero['level'],
  id=hero['id'],
  owner='player',
  x=-STARTX[i],
  y=STARTY[i]) for (i, hero) in enumerate(heroes) if hero is not None]


def get_enemy_state(stage):
  return [Hero.create_by_name(
  name='cube',
  level=1,
  id=-(i + 1),
  owner='enemy',
  x= STARTX[i],
  y= STARTY[i]) for i in range(3)]


def battle_is_over(turn):
  return (
      all(log_entry['loyalty'] <= 0 for log_entry in turn.values()) or
      all(log_entry['loyalty'] >= 0 for log_entry in turn.values()))


def get_winner(turn):
    if all(log_entry['loyalty'] <= 0 for log_entry in turn.values()):
      return -1
    elif all(log_entry['loyalty'] >= 0 for log_entry in turn.values()):
      return 1
    else:
      return 0


def simulate_battle(heroes, stage):
  state = get_player_state(heroes) + get_enemy_state(stage)
  livestate = state
  turns = [{hero.id: hero.get_log_entry() for hero in state}]
  while not battle_is_over(turns[-1]) and len(turns) < 120 * FPS / TURNFRAMES:
    for hero in livestate:
      hero.step(livestate, len(turns))
    for hero in livestate[:]:
      if getattr(hero, 'remove', False):
        livestate = livestate[:]
        livestate.remove(hero)
        hero.status.append({'type': 'Removed'})
        hero.loyalty = 0
    turns.append({hero.id: hero.get_log_entry() for hero in state})
  return turns
