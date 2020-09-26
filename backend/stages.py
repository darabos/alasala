import random
from backend import heroes

def generate():
  hs = heroes.Hero.get_index().values()
  for i in range(200):
    eligible = [h['classname'] for h in hs if h['min_stage'] <= i]
    levels = [1, 1, 1, 1, 1]
    for _ in range(i):
      levels[random.randrange(5)] += 1
    enemies = random.sample(eligible, 5)
    print('  dict(enemies=' + repr(list(zip(enemies, levels))) + '),')

if __name__ == '__main__':
  generate()

stages = [
  dict(enemies=[('Scientist', 1), ('Wizard', 1), ('Monkey', 1), ('BullLady', 1), ('Chicken', 1)]),
  dict(enemies=[('Wizard', 1), ('Monkey', 2), ('BullLady', 1), ('CursePrincess', 1), ('RescueParrot', 1)]),
  dict(enemies=[('RescueParrot', 1), ('CrocodileMan', 2), ('Wizard', 1), ('Scientist', 2), ('ThoughtWorm', 1)]),
  dict(enemies=[('Chicken', 2), ('BullLady', 1), ('ThoughtWorm', 3), ('InfectedSailor', 1), ('Scientist', 1)]),
  dict(enemies=[('CursePrincess', 2), ('Reaper', 3), ('Scientist', 2), ('CrocodileMan', 1), ('Monkey', 1)]),
  dict(enemies=[('RescueParrot', 2), ('BullLady', 2), ('CrocodileMan', 3), ('InfectedSailor', 2), ('CursePrincess', 1)]),
  dict(enemies=[('BullLady', 2), ('Monkey', 2), ('InfectedSailor', 1), ('Knight', 3), ('RescueParrot', 3)]),
  dict(enemies=[('BullLady', 2), ('CursePrincess', 3), ('Knight', 1), ('Monkey', 1), ('InfectedSailor', 5)]),
  dict(enemies=[('BullLady', 2), ('Scientist', 5), ('CursePrincess', 1), ('ThoughtWorm', 2), ('Knight', 3)]),
  dict(enemies=[('Chicken', 3), ('BullLady', 2), ('Scientist', 3), ('CursePrincess', 3), ('Reaper', 3)]),
  dict(enemies=[('Wizard', 1), ('ThoughtWorm', 2), ('CrocodileMan', 4), ('Monkey', 5), ('Knight', 3)]),
  dict(enemies=[('ThoughtWorm', 1), ('CursePrincess', 3), ('InfectedSailor', 3), ('Scientist', 3), ('Reaper', 6)]),
  dict(enemies=[('BullLady', 3), ('RescueParrot', 5), ('Scientist', 5), ('Knight', 2), ('CrocodileMan', 2)]),
  dict(enemies=[('Scientist', 6), ('BullLady', 3), ('CursePrincess', 2), ('InfectedSailor', 3), ('Reaper', 4)]),
  dict(enemies=[('BullLady', 5), ('ThoughtWorm', 2), ('Scientist', 1), ('RescueParrot', 8), ('Wizard', 3)]),
  dict(enemies=[('Reaper', 5), ('Scientist', 5), ('ThoughtWorm', 4), ('CursePrincess', 3), ('Chicken', 3)]),
  dict(enemies=[('Chicken', 3), ('Wizard', 5), ('Monkey', 3), ('Reaper', 6), ('BullLady', 4)]),
  dict(enemies=[('CrocodileMan', 2), ('BullLady', 2), ('Scientist', 4), ('Reaper', 7), ('ThoughtWorm', 7)]),
  dict(enemies=[('RescueParrot', 5), ('BullLady', 4), ('Monkey', 2), ('Scientist', 5), ('Chicken', 7)]),
  dict(enemies=[('RescueParrot', 3), ('BullLady', 2), ('Reaper', 2), ('InfectedSailor', 8), ('Wizard', 9)]),
  dict(enemies=[('CrocodileMan', 5), ('Wizard', 6), ('RescueParrot', 5), ('CursePrincess', 3), ('Knight', 6)]),
  dict(enemies=[('RescueParrot', 5), ('BullLady', 6), ('Knight', 5), ('Reaper', 4), ('Scientist', 6)]),
  dict(enemies=[('BullLady', 5), ('Wizard', 5), ('ThoughtWorm', 4), ('InfectedSailor', 9), ('CrocodileMan', 4)]),
  dict(enemies=[('Chicken', 7), ('InfectedSailor', 4), ('Wizard', 6), ('Knight', 6), ('ThoughtWorm', 5)]),
  dict(enemies=[('Reaper', 3), ('ThoughtWorm', 11), ('Chicken', 6), ('Monkey', 6), ('RescueParrot', 3)]),
  dict(enemies=[('InfectedSailor', 4), ('CrocodileMan', 5), ('CursePrincess', 5), ('BullLady', 8), ('ThoughtWorm', 8)]),
  dict(enemies=[('ThoughtWorm', 6), ('Knight', 7), ('Chicken', 4), ('CursePrincess', 8), ('RescueParrot', 6)]),
  dict(enemies=[('Monkey', 5), ('RescueParrot', 9), ('InfectedSailor', 6), ('CursePrincess', 6), ('Scientist', 6)]),
  dict(enemies=[('Knight', 5), ('CrocodileMan', 11), ('Wizard', 4), ('CursePrincess', 7), ('ThoughtWorm', 6)]),
  dict(enemies=[('CursePrincess', 9), ('BullLady', 4), ('InfectedSailor', 8), ('Reaper', 8), ('ThoughtWorm', 5)]),
  dict(enemies=[('Scientist', 10), ('CrocodileMan', 9), ('Knight', 5), ('Chicken', 4), ('BullLady', 7)]),
  dict(enemies=[('RescueParrot', 9), ('BullLady', 8), ('CursePrincess', 6), ('Wizard', 10), ('InfectedSailor', 3)]),
  dict(enemies=[('Chicken', 10), ('Scientist', 6), ('Reaper', 6), ('BullLady', 8), ('InfectedSailor', 7)]),
  dict(enemies=[('Scientist', 9), ('Reaper', 9), ('BullLady', 5), ('ThoughtWorm', 8), ('Knight', 7)]),
  dict(enemies=[('Reaper', 8), ('Scientist', 4), ('ThoughtWorm', 9), ('Chicken', 5), ('Monkey', 13)]),
  dict(enemies=[('ThoughtWorm', 8), ('Wizard', 9), ('Reaper', 12), ('Scientist', 6), ('RescueParrot', 5)]),
  dict(enemies=[('Monkey', 12), ('Reaper', 8), ('Scientist', 5), ('BullLady', 10), ('CursePrincess', 6)]),
  dict(enemies=[('RescueParrot', 8), ('CrocodileMan', 7), ('Chicken', 9), ('Monkey', 9), ('Scientist', 9)]),
  dict(enemies=[('RescueParrot', 8), ('CursePrincess', 8), ('Chicken', 8), ('CrocodileMan', 8), ('Reaper', 11)]),
  dict(enemies=[('Chicken', 10), ('Knight', 13), ('ThoughtWorm', 5), ('CursePrincess', 7), ('BullLady', 9)]),
  dict(enemies=[('CrocodileMan', 19), ('Scientist', 5), ('CursePrincess', 6), ('InfectedSailor', 4), ('Chicken', 11)]),
  dict(enemies=[('BullLady', 16), ('Wizard', 8), ('Reaper', 4), ('CursePrincess', 8), ('Monkey', 10)]),
  dict(enemies=[('RescueParrot', 11), ('Monkey', 7), ('InfectedSailor', 9), ('CursePrincess', 9), ('Chicken', 11)]),
  dict(enemies=[('BullLady', 9), ('Scientist', 7), ('Knight', 13), ('Wizard', 8), ('RescueParrot', 11)]),
  dict(enemies=[('Reaper', 12), ('Monkey', 12), ('Knight', 8), ('Wizard', 9), ('Chicken', 8)]),
  dict(enemies=[('Reaper', 10), ('CursePrincess', 16), ('CrocodileMan', 6), ('Chicken', 12), ('Wizard', 6)]),
  dict(enemies=[('RescueParrot', 13), ('Monkey', 9), ('CrocodileMan', 9), ('Scientist', 11), ('Reaper', 9)]),
  dict(enemies=[('InfectedSailor', 11), ('Monkey', 11), ('Knight', 10), ('Wizard', 10), ('CursePrincess', 10)]),
  dict(enemies=[('CrocodileMan', 10), ('InfectedSailor', 14), ('Knight', 14), ('Chicken', 8), ('RescueParrot', 7)]),
  dict(enemies=[('Scientist', 9), ('BullLady', 5), ('Reaper', 14), ('Chicken', 15), ('CursePrincess', 11)]),
  dict(enemies=[('RescueParrot', 11), ('Reaper', 9), ('ThoughtWorm', 16), ('Wizard', 10), ('Monkey', 9)]),
  dict(enemies=[('Reaper', 10), ('BullLady', 13), ('Knight', 9), ('RescueParrot', 12), ('Wizard', 12)]),
  dict(enemies=[('Wizard', 8), ('CrocodileMan', 18), ('BullLady', 12), ('Monkey', 12), ('CursePrincess', 7)]),
  dict(enemies=[('InfectedSailor', 14), ('Scientist', 14), ('Reaper', 7), ('Chicken', 12), ('CrocodileMan', 11)]),
  dict(enemies=[('InfectedSailor', 11), ('Wizard', 6), ('Scientist', 10), ('CrocodileMan', 20), ('CursePrincess', 12)]),
  dict(enemies=[('CrocodileMan', 12), ('InfectedSailor', 13), ('ThoughtWorm', 7), ('Chicken', 12), ('Scientist', 16)]),
  dict(enemies=[('Knight', 16), ('InfectedSailor', 9), ('Wizard', 13), ('ThoughtWorm', 14), ('Scientist', 9)]),
  dict(enemies=[('BullLady', 7), ('CrocodileMan', 20), ('ThoughtWorm', 10), ('Wizard', 15), ('InfectedSailor', 10)]),
  dict(enemies=[('ThoughtWorm', 11), ('RescueParrot', 14), ('BullLady', 16), ('Wizard', 11), ('Reaper', 11)]),
  dict(enemies=[('InfectedSailor', 12), ('Chicken', 9), ('Scientist', 13), ('Reaper', 19), ('CursePrincess', 11)]),
  dict(enemies=[('CrocodileMan', 15), ('Knight', 11), ('InfectedSailor', 12), ('Monkey', 12), ('RescueParrot', 15)]),
  dict(enemies=[('ThoughtWorm', 16), ('CrocodileMan', 14), ('InfectedSailor', 8), ('BullLady', 15), ('Knight', 13)]),
  dict(enemies=[('Reaper', 12), ('ThoughtWorm', 14), ('Scientist', 16), ('Chicken', 15), ('CursePrincess', 10)]),
  dict(enemies=[('Chicken', 13), ('CursePrincess', 12), ('RescueParrot', 18), ('BullLady', 8), ('ThoughtWorm', 17)]),
  dict(enemies=[('RescueParrot', 14), ('CrocodileMan', 17), ('Wizard', 18), ('Scientist', 9), ('Knight', 11)]),
  dict(enemies=[('CursePrincess', 17), ('Monkey', 14), ('ThoughtWorm', 10), ('BullLady', 12), ('Knight', 17)]),
  dict(enemies=[('CrocodileMan', 13), ('InfectedSailor', 9), ('Knight', 12), ('Scientist', 15), ('BullLady', 22)]),
  dict(enemies=[('InfectedSailor', 11), ('Scientist', 11), ('CrocodileMan', 17), ('BullLady', 16), ('Chicken', 17)]),
  dict(enemies=[('Scientist', 14), ('BullLady', 19), ('CursePrincess', 12), ('InfectedSailor', 15), ('CrocodileMan', 13)]),
  dict(enemies=[('Monkey', 19), ('Knight', 18), ('CursePrincess', 14), ('Reaper', 11), ('Wizard', 12)]),
  dict(enemies=[('Knight', 17), ('InfectedSailor', 11), ('BullLady', 12), ('Monkey', 17), ('Reaper', 18)]),
  dict(enemies=[('CrocodileMan', 22), ('Wizard', 15), ('InfectedSailor', 13), ('ThoughtWorm', 12), ('Knight', 14)]),
  dict(enemies=[('Wizard', 15), ('CursePrincess', 17), ('Knight', 11), ('Scientist', 18), ('RescueParrot', 16)]),
  dict(enemies=[('InfectedSailor', 15), ('Chicken', 8), ('Monkey', 17), ('Wizard', 15), ('Reaper', 23)]),
  dict(enemies=[('Scientist', 14), ('InfectedSailor', 15), ('Chicken', 12), ('CursePrincess', 21), ('CrocodileMan', 17)]),
  dict(enemies=[('Chicken', 17), ('CrocodileMan', 16), ('BullLady', 23), ('Reaper', 12), ('InfectedSailor', 12)]),
  dict(enemies=[('CursePrincess', 21), ('Reaper', 14), ('Wizard', 16), ('Monkey', 15), ('RescueParrot', 15)]),
  dict(enemies=[('Monkey', 18), ('ThoughtWorm', 15), ('Scientist', 21), ('InfectedSailor', 18), ('CursePrincess', 10)]),
  dict(enemies=[('CursePrincess', 20), ('Scientist', 12), ('ThoughtWorm', 18), ('Wizard', 18), ('RescueParrot', 15)]),
  dict(enemies=[('Wizard', 17), ('Reaper', 14), ('Knight', 17), ('CrocodileMan', 18), ('ThoughtWorm', 18)]),
  dict(enemies=[('BullLady', 21), ('Wizard', 12), ('ThoughtWorm', 15), ('Knight', 16), ('Reaper', 21)]),
  dict(enemies=[('Monkey', 19), ('BullLady', 12), ('Scientist', 21), ('Reaper', 12), ('Chicken', 22)]),
  dict(enemies=[('InfectedSailor', 13), ('CursePrincess', 20), ('Scientist', 18), ('Wizard', 17), ('Monkey', 19)]),
  dict(enemies=[('Chicken', 20), ('Monkey', 19), ('Wizard', 18), ('RescueParrot', 19), ('Reaper', 12)]),
  dict(enemies=[('Monkey', 25), ('Chicken', 11), ('CursePrincess', 11), ('Knight', 19), ('InfectedSailor', 23)]),
  dict(enemies=[('Reaper', 14), ('CursePrincess', 13), ('CrocodileMan', 15), ('Scientist', 24), ('Monkey', 24)]),
  dict(enemies=[('Knight', 21), ('ThoughtWorm', 8), ('Scientist', 17), ('Chicken', 21), ('RescueParrot', 24)]),
  dict(enemies=[('CursePrincess', 18), ('Knight', 16), ('Wizard', 14), ('Scientist', 21), ('CrocodileMan', 23)]),
  dict(enemies=[('ThoughtWorm', 17), ('InfectedSailor', 15), ('Scientist', 19), ('Chicken', 23), ('CrocodileMan', 19)]),
  dict(enemies=[('Chicken', 14), ('ThoughtWorm', 23), ('RescueParrot', 19), ('CrocodileMan', 14), ('Scientist', 24)]),
  dict(enemies=[('Knight', 20), ('BullLady', 22), ('Monkey', 20), ('RescueParrot', 18), ('Chicken', 15)]),
  dict(enemies=[('Wizard', 13), ('Chicken', 11), ('CrocodileMan', 26), ('Reaper', 23), ('CursePrincess', 23)]),
  dict(enemies=[('Scientist', 19), ('Monkey', 20), ('Wizard', 16), ('Reaper', 13), ('ThoughtWorm', 29)]),
  dict(enemies=[('Reaper', 26), ('InfectedSailor', 17), ('CrocodileMan', 17), ('RescueParrot', 17), ('Knight', 21)]),
  dict(enemies=[('Reaper', 24), ('RescueParrot', 15), ('Monkey', 26), ('InfectedSailor', 17), ('CursePrincess', 17)]),
  dict(enemies=[('RescueParrot', 17), ('Wizard', 20), ('Knight', 20), ('InfectedSailor', 25), ('Reaper', 18)]),
  dict(enemies=[('Monkey', 20), ('BullLady', 20), ('RescueParrot', 21), ('Scientist', 15), ('InfectedSailor', 25)]),
  dict(enemies=[('InfectedSailor', 23), ('BullLady', 14), ('Wizard', 21), ('Reaper', 22), ('Monkey', 22)]),
  dict(enemies=[('RescueParrot', 18), ('Knight', 25), ('CrocodileMan', 20), ('Chicken', 20), ('InfectedSailor', 20)]),
  dict(enemies=[('InfectedSailor', 17), ('CursePrincess', 18), ('BullLady', 26), ('RescueParrot', 27), ('Reaper', 16)]),
  dict(enemies=[('Chicken', 20), ('BullLady', 17), ('ThoughtWorm', 22), ('CursePrincess', 19), ('Knight', 27)]),
  dict(enemies=[('CrocodileMan', 21), ('CursePrincess', 27), ('Reaper', 25), ('Scientist', 18), ('Monkey', 15)]),
  dict(enemies=[('Knight', 14), ('RescueParrot', 22), ('CrocodileMan', 23), ('CursePrincess', 32), ('Wizard', 16)]),
  dict(enemies=[('Chicken', 23), ('ThoughtWorm', 21), ('Wizard', 23), ('CrocodileMan', 22), ('Knight', 19)]),
  dict(enemies=[('BullLady', 20), ('ThoughtWorm', 21), ('Wizard', 22), ('CrocodileMan', 25), ('Knight', 21)]),
  dict(enemies=[('Knight', 25), ('InfectedSailor', 23), ('BullLady', 26), ('RescueParrot', 18), ('CrocodileMan', 18)]),
  dict(enemies=[('Reaper', 26), ('Scientist', 25), ('Chicken', 21), ('CrocodileMan', 21), ('ThoughtWorm', 18)]),
  dict(enemies=[('Knight', 22), ('Scientist', 23), ('CrocodileMan', 18), ('Reaper', 27), ('ThoughtWorm', 22)]),
  dict(enemies=[('InfectedSailor', 18), ('Wizard', 20), ('Knight', 27), ('ThoughtWorm', 24), ('CursePrincess', 24)]),
  dict(enemies=[('InfectedSailor', 25), ('BullLady', 19), ('ThoughtWorm', 13), ('Chicken', 31), ('Scientist', 26)]),
  dict(enemies=[('Reaper', 28), ('Wizard', 18), ('ThoughtWorm', 24), ('Scientist', 21), ('Chicken', 24)]),
  dict(enemies=[('Monkey', 19), ('Wizard', 22), ('Knight', 25), ('Chicken', 24), ('CursePrincess', 26)]),
  dict(enemies=[('Monkey', 27), ('Chicken', 24), ('Knight', 23), ('ThoughtWorm', 19), ('CursePrincess', 24)]),
  dict(enemies=[('Knight', 15), ('Monkey', 27), ('ThoughtWorm', 25), ('CrocodileMan', 25), ('CursePrincess', 26)]),
  dict(enemies=[('Reaper', 28), ('Wizard', 19), ('RescueParrot', 28), ('Knight', 20), ('Scientist', 24)]),
  dict(enemies=[('CursePrincess', 27), ('BullLady', 15), ('Monkey', 24), ('ThoughtWorm', 29), ('Wizard', 25)]),
  dict(enemies=[('Scientist', 15), ('Reaper', 32), ('Knight', 24), ('CursePrincess', 26), ('BullLady', 24)]),
  dict(enemies=[('ThoughtWorm', 26), ('Wizard', 26), ('CrocodileMan', 24), ('RescueParrot', 24), ('Monkey', 22)]),
  dict(enemies=[('Monkey', 19), ('Knight', 33), ('Reaper', 28), ('ThoughtWorm', 20), ('Scientist', 23)]),
  dict(enemies=[('ThoughtWorm', 30), ('BullLady', 27), ('Wizard', 24), ('Scientist', 17), ('Chicken', 26)]),
  dict(enemies=[('Chicken', 26), ('CursePrincess', 18), ('BullLady', 34), ('CrocodileMan', 25), ('InfectedSailor', 22)]),
  dict(enemies=[('Reaper', 20), ('RescueParrot', 26), ('CursePrincess', 30), ('Scientist', 22), ('Chicken', 28)]),
  dict(enemies=[('Monkey', 22), ('Chicken', 20), ('ThoughtWorm', 22), ('CrocodileMan', 36), ('InfectedSailor', 27)]),
  dict(enemies=[('Monkey', 30), ('BullLady', 28), ('Chicken', 19), ('Wizard', 22), ('RescueParrot', 29)]),
  dict(enemies=[('Reaper', 23), ('BullLady', 35), ('Monkey', 26), ('RescueParrot', 24), ('Chicken', 21)]),
  dict(enemies=[('CursePrincess', 22), ('Scientist', 25), ('BullLady', 25), ('Knight', 31), ('InfectedSailor', 27)]),
  dict(enemies=[('Knight', 21), ('Chicken', 27), ('RescueParrot', 27), ('Reaper', 28), ('Scientist', 28)]),
  dict(enemies=[('Chicken', 25), ('Wizard', 25), ('RescueParrot', 27), ('Scientist', 33), ('Knight', 22)]),
  dict(enemies=[('ThoughtWorm', 26), ('Monkey', 26), ('InfectedSailor', 31), ('BullLady', 22), ('CrocodileMan', 28)]),
  dict(enemies=[('CursePrincess', 23), ('Knight', 27), ('Scientist', 24), ('CrocodileMan', 22), ('Reaper', 38)]),
  dict(enemies=[('InfectedSailor', 33), ('Monkey', 33), ('Reaper', 27), ('CursePrincess', 23), ('RescueParrot', 19)]),
  dict(enemies=[('Reaper', 35), ('CursePrincess', 27), ('Knight', 24), ('Wizard', 28), ('Monkey', 22)]),
  dict(enemies=[('CursePrincess', 35), ('ThoughtWorm', 25), ('InfectedSailor', 29), ('BullLady', 28), ('Reaper', 20)]),
  dict(enemies=[('Reaper', 33), ('InfectedSailor', 35), ('CursePrincess', 21), ('Wizard', 24), ('Monkey', 25)]),
  dict(enemies=[('Knight', 30), ('CrocodileMan', 21), ('Scientist', 34), ('Wizard', 22), ('Chicken', 32)]),
  dict(enemies=[('RescueParrot', 29), ('BullLady', 32), ('Wizard', 24), ('Reaper', 33), ('CursePrincess', 22)]),
  dict(enemies=[('Knight', 24), ('Monkey', 30), ('CursePrincess', 26), ('Chicken', 38), ('ThoughtWorm', 23)]),
  dict(enemies=[('ThoughtWorm', 36), ('CursePrincess', 20), ('RescueParrot', 38), ('Knight', 29), ('InfectedSailor', 19)]),
  dict(enemies=[('Wizard', 37), ('InfectedSailor', 27), ('CrocodileMan', 24), ('Monkey', 28), ('ThoughtWorm', 27)]),
  dict(enemies=[('Knight', 22), ('BullLady', 30), ('Monkey', 31), ('CrocodileMan', 31), ('ThoughtWorm', 30)]),
  dict(enemies=[('ThoughtWorm', 33), ('BullLady', 31), ('Knight', 27), ('Reaper', 28), ('Wizard', 26)]),
  dict(enemies=[('Monkey', 24), ('RescueParrot', 31), ('Wizard', 29), ('Knight', 28), ('BullLady', 34)]),
  dict(enemies=[('RescueParrot', 32), ('Scientist', 20), ('Reaper', 28), ('CrocodileMan', 23), ('Chicken', 44)]),
  dict(enemies=[('CrocodileMan', 23), ('Chicken', 36), ('RescueParrot', 29), ('Scientist', 40), ('BullLady', 20)]),
  dict(enemies=[('Knight', 40), ('Wizard', 24), ('Monkey', 22), ('Chicken', 32), ('Reaper', 31)]),
  dict(enemies=[('Knight', 33), ('CursePrincess', 34), ('Scientist', 26), ('Monkey', 26), ('InfectedSailor', 31)]),
  dict(enemies=[('Chicken', 26), ('BullLady', 36), ('InfectedSailor', 33), ('Knight', 28), ('CursePrincess', 28)]),
  dict(enemies=[('Reaper', 23), ('Wizard', 29), ('InfectedSailor', 33), ('RescueParrot', 39), ('Scientist', 28)]),
  dict(enemies=[('ThoughtWorm', 31), ('InfectedSailor', 34), ('RescueParrot', 37), ('CrocodileMan', 25), ('Chicken', 26)]),
  dict(enemies=[('Chicken', 35), ('RescueParrot', 29), ('CrocodileMan', 28), ('CursePrincess', 26), ('Wizard', 36)]),
  dict(enemies=[('CursePrincess', 24), ('Knight', 37), ('Reaper', 34), ('InfectedSailor', 36), ('Monkey', 24)]),
  dict(enemies=[('RescueParrot', 29), ('Monkey', 32), ('CursePrincess', 42), ('CrocodileMan', 25), ('InfectedSailor', 28)]),
  dict(enemies=[('Knight', 19), ('CursePrincess', 35), ('Wizard', 31), ('InfectedSailor', 37), ('CrocodileMan', 35)]),
  dict(enemies=[('Wizard', 27), ('Knight', 29), ('Scientist', 34), ('ThoughtWorm', 30), ('Reaper', 38)]),
  dict(enemies=[('CrocodileMan', 24), ('Knight', 29), ('InfectedSailor', 32), ('Wizard', 36), ('Reaper', 38)]),
  dict(enemies=[('Scientist', 26), ('Monkey', 40), ('Reaper', 33), ('Wizard', 31), ('InfectedSailor', 30)]),
  dict(enemies=[('ThoughtWorm', 29), ('CrocodileMan', 29), ('Reaper', 29), ('InfectedSailor', 44), ('Knight', 30)]),
  dict(enemies=[('Scientist', 32), ('Wizard', 40), ('RescueParrot', 34), ('BullLady', 30), ('CrocodileMan', 26)]),
  dict(enemies=[('Knight', 25), ('ThoughtWorm', 40), ('Reaper', 42), ('Wizard', 30), ('RescueParrot', 26)]),
  dict(enemies=[('Monkey', 30), ('ThoughtWorm', 24), ('Scientist', 38), ('InfectedSailor', 38), ('Chicken', 34)]),
  dict(enemies=[('ThoughtWorm', 35), ('Scientist', 41), ('Knight', 31), ('InfectedSailor', 24), ('Wizard', 34)]),
  dict(enemies=[('Reaper', 32), ('RescueParrot', 31), ('Monkey', 33), ('Wizard', 28), ('Knight', 42)]),
  dict(enemies=[('Knight', 45), ('Chicken', 35), ('CrocodileMan', 26), ('RescueParrot', 31), ('CursePrincess', 30)]),
  dict(enemies=[('Wizard', 33), ('Chicken', 28), ('Monkey', 38), ('BullLady', 30), ('CursePrincess', 39)]),
  dict(enemies=[('BullLady', 41), ('RescueParrot', 34), ('ThoughtWorm', 33), ('Monkey', 35), ('Reaper', 26)]),
  dict(enemies=[('ThoughtWorm', 32), ('Knight', 26), ('Chicken', 34), ('Scientist', 39), ('Wizard', 39)]),
  dict(enemies=[('ThoughtWorm', 33), ('Reaper', 38), ('CrocodileMan', 36), ('Chicken', 35), ('Scientist', 29)]),
  dict(enemies=[('Wizard', 28), ('Monkey', 36), ('Chicken', 34), ('BullLady', 38), ('Reaper', 36)]),
  dict(enemies=[('Reaper', 36), ('Scientist', 36), ('ThoughtWorm', 27), ('Knight', 32), ('RescueParrot', 42)]),
  dict(enemies=[('CursePrincess', 33), ('Monkey', 38), ('InfectedSailor', 36), ('Knight', 30), ('Wizard', 37)]),
  dict(enemies=[('CursePrincess', 37), ('Reaper', 39), ('Scientist', 39), ('Chicken', 26), ('CrocodileMan', 34)]),
  dict(enemies=[('InfectedSailor', 36), ('ThoughtWorm', 34), ('BullLady', 38), ('Monkey', 38), ('RescueParrot', 30)]),
  dict(enemies=[('RescueParrot', 32), ('Knight', 43), ('BullLady', 40), ('Scientist', 30), ('Reaper', 32)]),
  dict(enemies=[('CursePrincess', 22), ('Knight', 38), ('ThoughtWorm', 33), ('InfectedSailor', 52), ('Reaper', 33)]),
  dict(enemies=[('ThoughtWorm', 44), ('CursePrincess', 33), ('BullLady', 41), ('Scientist', 32), ('Reaper', 29)]),
  dict(enemies=[('Chicken', 42), ('InfectedSailor', 35), ('Scientist', 27), ('Wizard', 46), ('ThoughtWorm', 30)]),
  dict(enemies=[('BullLady', 32), ('CrocodileMan', 36), ('Scientist', 33), ('Monkey', 39), ('InfectedSailor', 41)]),
  dict(enemies=[('Knight', 38), ('RescueParrot', 35), ('Wizard', 46), ('Scientist', 27), ('Monkey', 36)]),
  dict(enemies=[('Knight', 37), ('Chicken', 34), ('CursePrincess', 38), ('BullLady', 39), ('RescueParrot', 35)]),
  dict(enemies=[('RescueParrot', 39), ('Monkey', 26), ('BullLady', 40), ('InfectedSailor', 36), ('ThoughtWorm', 43)]),
  dict(enemies=[('InfectedSailor', 31), ('Wizard', 41), ('Monkey', 41), ('Chicken', 33), ('Scientist', 39)]),
  dict(enemies=[('RescueParrot', 36), ('Wizard', 38), ('Knight', 40), ('Reaper', 41), ('InfectedSailor', 31)]),
  dict(enemies=[('CrocodileMan', 40), ('Reaper', 32), ('Wizard', 30), ('CursePrincess', 46), ('InfectedSailor', 39)]),
  dict(enemies=[('BullLady', 34), ('Reaper', 40), ('ThoughtWorm', 47), ('Wizard', 38), ('Knight', 29)]),
  dict(enemies=[('ThoughtWorm', 37), ('CrocodileMan', 33), ('Reaper', 41), ('RescueParrot', 37), ('Scientist', 41)]),
  dict(enemies=[('Chicken', 40), ('Wizard', 46), ('InfectedSailor', 42), ('CursePrincess', 30), ('Scientist', 32)]),
  dict(enemies=[('CursePrincess', 30), ('Monkey', 39), ('InfectedSailor', 34), ('CrocodileMan', 42), ('RescueParrot', 46)]),
  dict(enemies=[('BullLady', 39), ('Wizard', 32), ('Monkey', 47), ('ThoughtWorm', 40), ('CrocodileMan', 34)]),
  dict(enemies=[('BullLady', 41), ('InfectedSailor', 41), ('Chicken', 28), ('RescueParrot', 46), ('Wizard', 37)]),
  dict(enemies=[('ThoughtWorm', 39), ('Scientist', 39), ('Knight', 47), ('InfectedSailor', 38), ('Reaper', 31)]),
  dict(enemies=[('Scientist', 46), ('Chicken', 27), ('CursePrincess', 39), ('Monkey', 50), ('InfectedSailor', 33)]),
  dict(enemies=[('Wizard', 43), ('ThoughtWorm', 29), ('Reaper', 40), ('CrocodileMan', 38), ('Chicken', 46)]),
  dict(enemies=[('Monkey', 37), ('Reaper', 45), ('Chicken', 35), ('BullLady', 47), ('Knight', 33)]),
  dict(enemies=[('Monkey', 49), ('Chicken', 36), ('CrocodileMan', 39), ('CursePrincess', 34), ('RescueParrot', 40)]),
  dict(enemies=[('Wizard', 37), ('CrocodileMan', 44), ('Chicken', 39), ('Knight', 40), ('BullLady', 39)]),
  dict(enemies=[('RescueParrot', 37), ('Reaper', 36), ('InfectedSailor', 44), ('Knight', 42), ('Wizard', 41)]),
  dict(enemies=[('RescueParrot', 46), ('Chicken', 37), ('BullLady', 28), ('InfectedSailor', 48), ('Scientist', 42)]),
  dict(enemies=[('CursePrincess', 38), ('Reaper', 44), ('Monkey', 40), ('Wizard', 46), ('Scientist', 34)]),
  dict(enemies=[('Monkey', 38), ('Chicken', 40), ('Scientist', 46), ('CrocodileMan', 29), ('Reaper', 50)]),
  dict(enemies=[('Monkey', 40), ('ThoughtWorm', 51), ('RescueParrot', 39), ('CrocodileMan', 34), ('InfectedSailor', 40)]),
]
