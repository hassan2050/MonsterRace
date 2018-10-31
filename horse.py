#! /usr/bin/env python3

import os, sys, string, time, logging, argparse
import glob

import pygame
#import pygame_sdl2 as pygame

from PIL import Image

import AnimatedSprite
import BlinkingLED
try:
    import dispense
except:
  import dispensenull as dispense

try:
  import RPi.GPIO as GPIO
except:
  import nullgpio as GPIO

try:
  import config
except ImportError:
  print ("no config.py found.  Please copy sample_config.py to config.py.")
  sys.exit(1)

if 0:
  x = 0
  y = 0
#os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)
if 0:
  os.environ['SDL_VIDEODRIVER'] = "fbcon"
  os.putenv('SDL_FBDEV','/dev/fb0')
  os.environ["SDL_FBDEV"] = "/dev/fb0"


SONG_END = pygame.USEREVENT + 1

BLACK = (0,0,0)
WHITE = (255,255,255)

class Horse:
    def __init__(self, horseid, name,leds):
        self.name = name
        self.horseid = horseid
        self.slotnumber = horseid+1
        self.leds = leds
        dispense.dispense_init()

        horsePath = os.path.join(config.imagePath, 'horse_%d' % (self.slotnumber))

        im = pygame.image.load(os.path.join(horsePath, 'still.png'))

        w,h = im.get_size(); ratio = w/h
        height = config.horsesize[1]
        if self.horseid == 0: height = int(height * .8 * .85)
        else: height = int(height * .95)
        im = pygame.transform.scale(im, (int(height * ratio), height))

        self.still = im

        files = glob.glob(os.path.join(horsePath, "frame*.png"))
        files.sort()
        frames = []
        for fn in files:
           im = pygame.image.load(fn).convert_alpha()

           w,h = im.get_size(); ratio = w/h
           height = config.horsesize[1]
           if self.horseid == 0: height = int(height * .8)
           im = pygame.transform.scale(im, (int(height * ratio), height))

           frames.append(im)
          
        self.sprite = AnimatedSprite.AnimatedSprite(frames)
        self.blinkingLEDs = BlinkingLED.BlinkingLED(GPIO,self.leds[0],self.leds[1],animation_time=0.2)

        im = pygame.image.load(os.path.join(horsePath, 'face.png')).convert_alpha()
        self.character = pygame.transform.scale(im, (200,200))

        self.reset()

    def hide(self): self.hidden = True
    def show(self): self.hidden = False

    def reset(self):
      
        dx = (4-self.horseid)*60
        self.x = 40 + dx
        self.finishlinex = config.finishlinex + dx
        
        dy = (980-620) // 3
        self.y = 620 + (self.horseid) * dy

        self.feet = 0
        self.done = False
        self.hide()

        self.startTime = None
        self.endTime = None
        self.setLEDs()

    def reset_time(self):
        self.startTime = time.time()
        self.endTime = time.time()

    def draw(self, screen, dt):
      if self.hidden: return
      if self.done or self.startTime is None:
        screen.blit(self.still, [self.x, self.y-self.sprite.images[self.sprite.index].get_size()[1]])
      else:
        self.sprite.update(dt,screen,self.x, self.y-self.sprite.images[self.sprite.index].get_size()[1])
        if not self.done:
          if self.x >= self.finishlinex:
            self.done = True
            self.endTime = time.time()

    def updateLEDs(self,dt):
        if self.hidden:
            self.blinkingLEDs.update(dt)

    def setLEDs(self):
        #print('setLEDs')
        if self.x >= self.finishlinex:
             GPIO.output(self.leds[0],0)
             GPIO.output(self.leds[1],0)
             #print('setLEDs: self.x < config.finishlinex',self.x,config.finishlinex)
        else:
          if (self.feet==0):
             GPIO.output(self.leds[0],0)
             GPIO.output(self.leds[1],1)
          else:
             GPIO.output(self.leds[1],0)
             GPIO.output(self.leds[0],1)

    def change_state(self):
        GPIO.output(self.leds[0],0)
        GPIO.output(self.leds[1],0)

    def button(self, paw):
        if self.hidden:
            return
        if self.x < self.finishlinex:
            if self.feet == 0:
              if paw == 0:
                self.x += config.horsesize[0]//10
                self.feet=1
            elif self.feet == 1:
              if paw == 1:
                self.x += config.horsesize[0]//10
                self.feet=0
        elif self.x >= self.finishlinex:
            self.timerStarted = False
        self.setLEDs()

class Grass:
  def __init__(self):
    self.grass = pygame.image.load(os.path.join(config.imagePath, 'background_3.png'))

  def draw(self, screen, pos):
    screen.blit(self.grass, pos)

class Grass2:
  def __init__(self):
    self.track = pygame.image.load(os.path.join(config.imagePath, 'track.png'))

  def draw(self, screen, pos):
    x = pos[0]
    y = pos[1]

    screen.blit(self.track, [x, y])

  def update(self, screen, pos):
    x = 100
    y = 620 - config.horsesize[1]
    area = pygame.Rect((x,y), (config.screensize[0], 980))
    screen.blit(self.track, [x, y], area)


class States(object):
    def __init__(self):
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None

class Splash(States):
    def __init__(self, app):
        self.app = app
        States.__init__(self)
        self.next = 'start'

    def startup(self):
        logging.debug('starting Splash state')
        self.timerStarted = True
        self.time = 3

    def get_event(self, event):
        if event.type == pygame.JOYBUTTONUP:
          logging.debug("Joystick button released.")
          logging.debug(event)
        elif event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE: self.quit = True
          elif event.key == pygame.K_SPACE: self.done = True

    def update(self, screen, dt):
        if dt > 1: dt = 0
        self.draw(screen, dt)
        if self.timerStarted == True:
            self.time = self.time - dt
        if self.time < 0 and self.timerStarted == True:
            self.done = True
    def draw(self, screen, dt):
            screen.blit(self.app.title, [0,0])

class Start(States):
    def __init__(self, app):
        self.app = app
        States.__init__(self)
        self.next = 'countdown'

    def startup(self):
        self.timerStarted = False
        self.time = 3
        self.app.resetHorses()
        logging.debug('starting Start state')

        self.myfont = pygame.font.SysFont(os.path.join(config.fontPath, 'Bebas Neue.ttf'), 60)
        self.myfont2 = pygame.font.SysFont(os.path.join(config.fontPath, 'Bebas Neue.ttf'), 40)

    def get_event(self, event):
        if event.type == pygame.JOYBUTTONUP:
            logging.debug("Joystick button released.")
            logging.debug(event)
            if event.button==0: self.app.addHorse(0)
            elif event.button==1: self.app.addHorse(0)
            elif event.button==2: self.app.addHorse(1)
            elif event.button==3: self.app.addHorse(1)
            elif event.button==4: self.app.addHorse(2)
            elif event.button==5: self.app.addHorse(2)
            elif event.button==6: self.app.addHorse(3)
            elif event.button==7: self.app.addHorse(3)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.quit = True
            elif event.key == pygame.K_3: self.app.addHorse(0)
            elif event.key == pygame.K_e: self.app.addHorse(1)
            elif event.key == pygame.K_d: self.app.addHorse(2)
            elif event.key == pygame.K_c: self.app.addHorse(3)
            elif event.key == pygame.K_y: self.app.addHorse(4)
            elif event.key == pygame.K_h: self.app.addHorse(5)

        if self.app.numPeople() >= config.minpeople:
          self.timerStarted = True
        if self.app.numPeople() == len(config.horseNames):
            self.done = True

    def update(self, screen, dt):
        self.draw(screen, dt)
        if self.timerStarted == True:
            self.time = self.time - dt
        if self.time < 0 and self.timerStarted == True:
            self.done = True
        for horse in self.app._horses:
            horse.updateLEDs(dt)

    def draw(self, screen, dt):
        screen.blit(self.app.results2, [0,0])
        
        mx = 100
        dx = (config.screensize[0]-mx*2) // 4


        for n, horse in enumerate(self.app._horses):
          r = pygame.Rect((0,0), (dx-10,dx-10))
          r.x = (n * dx) + mx
          r.y = (config.screensize[1]-dx) // 2

          cx = r.x + dx//2

          pygame.draw.rect(screen, WHITE, r, 0)
          pygame.draw.rect(screen, BLACK, r, 3)

          y = r.y
          y += 30
          screen.blit(horse.character, (cx-(horse.character.get_size()[0])//2, y))

          r2 = horse.character.get_rect()
          r2.x = cx-(horse.character.get_size()[0])//2
          r2.y = y
          pygame.draw.rect(screen, BLACK, r2, 2)

          y += horse.character.get_size()[1] 
          y += 5

          textsurface = self.myfont2.render(horse.name, True, BLACK)
          screen.blit(textsurface, (cx - textsurface.get_size()[0]//2, y))
          
          y += textsurface.get_size()[1]

          if horse.hidden:
              textsurface = self.myfont.render('Press Any', True, BLACK)
              screen.blit(textsurface, (cx - textsurface.get_size()[0]//2, y))
              y += textsurface.get_size()[1]
              textsurface = self.myfont.render('Button', True, BLACK)
              screen.blit(textsurface, (cx - textsurface.get_size()[0]//2, y))
              y += textsurface.get_size()[1]

              if self.timerStarted == True:
                textsurface = self.myfont.render(str(round(self.time)), True, BLACK)
                screen.blit(textsurface, (cx - textsurface.get_size()[0]//2, y))
          else:
              textsurface = self.myfont.render('Ready!', True, BLACK)
              screen.blit(textsurface, (cx - textsurface.get_size()[0]//2, y+50))

class CountDown(States):
    def __init__(self, app):
        self.app = app
        States.__init__(self)
        self.next = 'game'

    def startup(self):
        self.myfont = pygame.font.SysFont(os.path.join(config.fontPath, 'Bebas Neue.ttf'), 60)

        files = glob.glob(os.path.join(config.imagePath, 'countdown*.png'))
        files.sort()

        frames = []
        for fn in files:
           im = pygame.image.load(fn).convert_alpha()

           w,h = im.get_size(); ratio = w/h
           im = pygame.transform.scale(im, (w*4, h*4))
           frames.append(im)

        self.sprite=AnimatedSprite.AnimatedSprite(frames, index=5, offset=-1,animation_time=1)
        self.timerStarted = True
        self.time = 6

        logging.debug('starting Countdown state')
        pygame.mixer.music.load(os.path.join(config.soundPath, 'racestart.ogg'))
        pygame.mixer.music.set_endevent(SONG_END)
        pygame.mixer.music.play(0)

        for horse in self.app.horses():
            horse.setLEDs()

    def get_event(self, event):
        if event.type == pygame.JOYBUTTONUP:
            logging.debug("Joystick button released.")
            logging.debug(event)
            if event.button==0: self.app.addHorse(0)
            elif event.button==1: self.app.addHorse(0)
            elif event.button==2: self.app.addHorse(1)
            elif event.button==3: self.app.addHorse(1)
            elif event.button==4: self.app.addHorse(2)
            elif event.button==5: self.app.addHorse(2)
            elif event.button==6: self.app.addHorse(3)
            elif event.button==7: self.app.addHorse(3)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.quit = True
            elif event.key == pygame.K_3: self.app.addHorse(0)
            elif event.key == pygame.K_e: self.app.addHorse(1)
            elif event.key == pygame.K_d: self.app.addHorse(2)
            elif event.key == pygame.K_c: self.app.addHorse(3)
            elif event.key == pygame.K_y: self.app.addHorse(4)
            elif event.key == pygame.K_h: self.app.addHorse(5)

    def update(self, screen, dt):
        self.draw(screen, dt)
        for horse in self.app._horses:
            horse.updateLEDs(dt)
        if self.timerStarted == True:
            self.time = self.time - dt
        if self.time < 0 and self.timerStarted == True:
            self.done = True

    def draw(self, screen, dt):
        self.app.grass.draw(screen, [0,0])

        if self.timerStarted == True:
            self.sprite.update(dt, screen,
                               x=(config.screensize[0] - self.sprite.images[self.sprite.index].get_size()[0])//2,
                               y=(config.screensize[1] - self.sprite.images[self.sprite.index].get_size()[1])//2)


        for horse in self.app.horses():
          horse.draw(screen, dt)
          if not horse.hidden:
            textsurface = self.myfont.render(str(horse.slotnumber), True, BLACK)
            screen.blit(textsurface, (horse.finishlinex+60, horse.y-45-(textsurface.get_size()[1])//2))

            pygame.draw.line(screen, BLACK, 
                             (horse.finishlinex, horse.y), 
                             (horse.finishlinex+60, horse.y-90), 10)

class Game(States):
    def __init__(self, app):
        self.app = app
        States.__init__(self)
        self.next = 'finish'


    def startup(self):
        self.myfont = pygame.font.SysFont(os.path.join(config.fontPath, 'Bebas Neue.ttf'), 60)

        files = glob.glob(os.path.join(config.imagePath, 'countdownend*.png'))
        files.sort()
        files.append(os.path.join(config.imagePath, 'endgame.png'))

        frames = []
        for fn in files:
           im = pygame.image.load(fn).convert_alpha()

           w,h = im.get_size(); ratio = w/h
           im = pygame.transform.scale(im, (w*4, h*4))
           frames.append(im)

        self.sprite = AnimatedSprite.AnimatedSprite(frames, index=5, offset=-1, animation_time=1)
        self.timerStarted = False
        self.time = 5
        for horse in self.app.horses():
            horse.reset_time()
            horse.setLEDs()
        logging.debug('starting Game state')

    def get_event(self, event):
          if event.type == SONG_END:
            logging.debug("the song ended!")
            pygame.mixer.music.load(os.path.join(config.soundPath, 'horsesounds.ogg'))
            pygame.mixer.music.play(0)

          if event.type == pygame.JOYBUTTONUP:
            logging.debug("Joystick button released.")
            logging.debug(event)
            if   event.button==0: self.app.getHorse(0).button(0)
            elif event.button==1: self.app.getHorse(0).button(1)
            elif event.button==2: self.app.getHorse(1).button(0)
            elif event.button==3: self.app.getHorse(1).button(1)
            elif event.button==4: self.app.getHorse(2).button(0)
            elif event.button==5: self.app.getHorse(2).button(1)
            elif event.button==6: self.app.getHorse(3).button(0)
            elif event.button==7: self.app.getHorse(3).button(1)
          elif event.type == pygame.KEYDOWN:
            if   event.key == pygame.K_1: self.app.getHorse(0).button(0)
            elif event.key == pygame.K_2: self.app.getHorse(0).button(1)
            elif event.key == pygame.K_q: self.app.getHorse(1).button(0)
            elif event.key == pygame.K_w: self.app.getHorse(1).button(1)
            elif event.key == pygame.K_a: self.app.getHorse(2).button(0)
            elif event.key == pygame.K_s: self.app.getHorse(2).button(1)
            elif event.key == pygame.K_z: self.app.getHorse(3).button(0)
            elif event.key == pygame.K_x: self.app.getHorse(3).button(1)
            elif event.key == pygame.K_ESCAPE:
              self.quit = True

    def update(self, screen, dt):
        self.draw(screen, dt)

        if self.timerStarted == True:
            self.time = self.time - dt
        horses = self.app.horses()

        if not self.timerStarted:
          for horse in horses:
            if horse.done:
              self.timerStarted = True

        ## check if all of the horse are done
        if self.timerStarted:
          dones = [horse.done for horse in horses if not horse.done]
          if len(dones) == 0:
            self.done = True

          ## check if the finish timer has run out
          if self.time < 0: self.done = True

    def draw(self, screen, dt):
        self.app.grass.update(screen, [0,0])

        horses = self.app.horses()
        for horse in horses:

          if not horse.hidden:
            textsurface = self.myfont.render(str(horse.slotnumber), True, BLACK)
            screen.blit(textsurface, (horse.finishlinex+60, horse.y-45-(textsurface.get_size()[1])//2))

            pygame.draw.line(screen, BLACK, 
                             (horse.finishlinex, horse.y), 
                             (horse.finishlinex+60, horse.y-90), 10)

          horse.draw(screen, dt)

        if self.timerStarted == True:
          self.sprite.update(dt, screen,
                             x=(config.screensize[0] - self.sprite.images[self.sprite.index].get_size()[0])//2,
                             y=(config.screensize[1] - self.sprite.images[self.sprite.index].get_size()[1])//2)



class Finish(States):
    def __init__(self, app):
        self.app = app
        States.__init__(self)
        self.next = 'candy'
        self.showTimer = None

    def startup(self):
        logging.debug('starting Finish state')

        self.myfont = pygame.font.SysFont(os.path.join(config.fontPath, 'Bebas Neue.ttf'), 80)

        pygame.mixer.music.load(os.path.join(config.soundPath, 'finish.ogg'))
        pygame.mixer.music.play(0)
        self.sortedList = sorted(self.app.horses(), key=lambda horse: (not horse.done, horse.endTime-horse.startTime, horse.x))
        #file = open(“testfile.txt”,”w+”)
        #file.write(self.sortedList)
        #file.close()
        result_str=""
        for horse in self.app._horses:
            if (horse.hidden):
               result_str=result_str+"DNR,"
            else:
               result_str=result_str+"{0:.2f},".format(horse.endTime - horse.startTime)
        logging.debug("LOGLINE: %s" % result_str)
        file = open("logfile.csv","a")
        file.write(result_str+"\n")
        file.close()

        for horse in self.app.horses():
          dt = horse.endTime - horse.startTime
          logging.info("%d: %.3f" % ((horse.slotnumber), dt))
          logging.debug("%d: %.3f" % ((horse.slotnumber), dt))
        self.dispensed_candy = False
##           if dt == 0:
##             horse.endTime = None

    def get_event(self, event):
        if event.type == pygame.JOYBUTTONUP:
          logging.debug("Joystick button released.")
          logging.debug(event)
          if event.button in (0,2,4,6):
            self.markDone()
        elif event.type == pygame.MOUSEBUTTONDOWN:
          self.markDone()
        elif event.type == pygame.KEYDOWN:
          if event.key in (pygame.K_1, pygame.K_q, pygame.K_a, pygame.K_z):
            self.markDone()
          elif event.key == pygame.K_ESCAPE: self.quit = True
    def markDone(self):
        logging.debug("markDone")
      #dt = time.time() - self.showTimer
    def update(self, screen, dt):
        self.draw(screen)
        pygame.display.flip()

    def draw(self, screen):
        screen.blit(self.app.results2, [0,0])

        mx = 100
        dx = (config.screensize[0]-mx*2) // 4


        for place, horse in enumerate(self.sortedList):
          if horse.hidden: continue

          r = pygame.Rect((0,0), (dx-10,dx-10))
          r.x = (horse.horseid * dx) + mx
          r.y = (config.screensize[1]-dx) // 2

          cx = r.x + dx//2

          pygame.draw.rect(screen, WHITE, r, 0)
          pygame.draw.rect(screen, BLACK, r, 3)

          y = r.y
          y += 30

          screen.blit(horse.character, (cx-(horse.character.get_size()[0])//2, y))

          r2 = horse.character.get_rect()
          r2.x = cx-(horse.character.get_size()[0])//2
          r2.y = y
          pygame.draw.rect(screen, BLACK, r2, 2)

          y += horse.character.get_size()[1] 
          y += 20

          if 0:
            logging.debug((col,row))
            logging.debug("%s %s %s" % (horse.slotnumber, horse.endTime-horse.startTime, horse.x))
            logging.debug("%s %s" % (horse.name,place))

          if not horse.done:
            textsurface = self.myfont.render('DNF', True, BLACK)
          else:
            textsurface = self.myfont.render(str(round((horse.endTime-horse.startTime),2)), True, BLACK)

          screen.blit(textsurface, (cx - textsurface.get_size()[0]/2, y+70))

          ribbon = self.app.ribbons[place]
          ribbon_rect = ribbon.get_rect()
          ribbon_rect.x = cx + horse.character.get_size()[0]//2 - ribbon_rect.width//2
          ribbon_rect.y = y-100

          screen.blit(ribbon, ribbon_rect)

        self.done = True


class Candy(States):
    def __init__(self, app):
        self.app = app
        States.__init__(self)
        self.next = 'splash'
        self.showTimer = None

    def startup(self):
        self.sortedList = sorted(self.app.horses(), key=lambda horse: (not horse.done, horse.endTime-horse.startTime, horse.x))
        logging.debug('starting Candy state')
        self.dispensed_candy = False
##           if dt == 0:
##             horse.endTime = None

    def get_event(self, event):
        if event.type == pygame.JOYBUTTONUP:
          logging.debug("Joystick button released.")
          logging.debug(event)
          if event.button in (0,2,4,6):
            self.markDone()
        elif event.type == pygame.MOUSEBUTTONDOWN:
          self.markDone()
        elif event.type == pygame.KEYDOWN:
          if event.key in (pygame.K_1, pygame.K_q, pygame.K_a, pygame.K_z):
            self.markDone()
          elif event.key == pygame.K_ESCAPE: self.quit = True
    def markDone(self):
      dt = time.time() - self.showTimer
      if dt > 5:
        self.done = True
    def update(self, screen, dt):
        self.draw(screen)
        pygame.display.flip()
    def draw(self, screen):
        if not self.dispensed_candy:
              winner = self.sortedList[0].horseid
              #print("The winner is " + str(winner+1))
              for horse in self.app.horses():
                dispense.dispense_back(horse.horseid)
              time.sleep(2)
              for horse in self.app.horses():
                dispense.dispense_forward(horse.horseid)
              time.sleep(2)
              dispense.dispense_back(winner)
              time.sleep(2)
              dispense.dispense_forward(winner)
              self.showTimer = time.time()
              self.dispensed_candy = True
        self.done = True

class HorseApp:
    def __init__(self, **settings):
        self.__dict__.update(settings)
        self.done = False
        self.state = None
        self.state_name = None
        self.state_dict = None

        self.screen = pygame.display.set_mode(config.screensize, pygame.FULLSCREEN|pygame.DOUBLEBUF|pygame.HWSURFACE)
        #self.screen = pygame.display.set_mode(config.screensize, pygame.DOUBLEBUF|pygame.HWSURFACE)

        try:
            GPIO.setsurface(self.screen)
            # Method exists, and was used.
        except AttributeError:
            # Method does not exist.  What now?
            logging.debug('traditional GPIO')

        self.clock = pygame.time.Clock()
        self._horses = []
        for horsenum, name in enumerate(config.horseNames):
          self._horses.append(Horse(horsenum, name,config.horseLeds[horsenum]))

    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
        self.state.startup()

    def flip_state(self):
        for horse in self._horses:
            horse.change_state()
        self.state.done = False
        previous,self.state_name = self.state_name, self.state.next
        self.state = self.state_dict[self.state_name]
        self.state.startup()
        self.state.previous = previous

    def horses(self):
      horses = [horse for horse in self._horses if not horse.hidden]
      return horses

    def getHorse(self, horseid):
      return self._horses[horseid]

    def numPeople(self):
      return len(self.horses())

    def addHorse(self, horseid):
      if self._horses[horseid].hidden:
        logging.debug('Player %d joined' % horseid)
        logging.debug('There are %d people ready' % self.numPeople())
      self._horses[horseid].show()

    def resetHorses(self):
      for horse in self._horses:
        horse.reset()

    def update(self, dt):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(self.screen, dt)

    def event_loop(self):
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.done = True
        self.state.get_event(event)

    def main_game_loop(self):
      self.myfont = pygame.font.SysFont(os.path.join(config.fontPath, 'Bebas Neue.ttf'), 30)

      while not self.done:
        delta_time = self.clock.tick(self.fps)/1000.0
        self.event_loop()
        self.update(delta_time)

        if 1:
          #fps = delta_time * 60
          fps = 1./delta_time
          textsurface = self.myfont.render("fps: %.1f" % fps, True, BLACK)
          pygame.draw.rect(self.screen, WHITE, (0, 0, textsurface.get_size()[0], textsurface.get_size()[1]), 0)
          self.screen.blit(textsurface, (0, 0))

        pygame.display.update()
        pygame.display.flip()

            


def start():
  settings = {
      'size': config.tracksize,
      'fps' : 60
  }

  #
  # Setup GPIO pins for LEDs
  #
  if 1:
    GPIO.setmode(GPIO.BCM)
    for io in config.horseLeds:
      GPIO.setup(io,GPIO.OUT)

  #app = HorseApp(**settings)
  app = HorseApp(**settings)

  state_dict = {
      'splash': Splash(app),
      'start': Start(app),
      'countdown': CountDown(app),
      'game': Game(app),
      'finish':Finish(app),
      'candy':Candy(app)
  }

  pygame.init()
  pygame.joystick.init()
  joystick_count = pygame.joystick.get_count()
  for i in range(joystick_count):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()

  pygame.mouse.set_visible(False)
  app.title = pygame.image.load(os.path.join(config.imagePath, 'splash.png')).convert_alpha()
  app.results2 = pygame.image.load(os.path.join(config.imagePath, 'results.png')).convert_alpha()

  app.ribbons = []
  for n in range(4):
    im = pygame.image.load(os.path.join(config.imagePath, 'ribbons', 'ribbon%d.png' % (n+1))).convert_alpha()
    w,h = im.get_size(); ratio = w/h
    im = pygame.transform.scale(im, (int(200 * ratio), 200))
    app.ribbons.append(im)

  app.grass = Grass2()

  app.setup_states(state_dict, 'splash')
  app.main_game_loop()
  pygame.quit()


def parse_args(argv):
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description=__doc__)

  parser.add_argument("-t", "--test", dest="test_flag",
                    default=False,
                    action="store_true",
                    help="Run test function")
  parser.add_argument("--log-level", type=str,
                      choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      help="Desired console log level")
  parser.add_argument("-d", "--debug", dest="log_level", action="store_const",
                      const="DEBUG",
                      help="Activate debugging")
  parser.add_argument("-q", "--quiet", dest="log_level", action="store_const",
                      const="CRITICAL",
                      help="Quite mode")
  #parser.add_argument("files", type=str, nargs='+')

  args = parser.parse_args(argv[1:])
  if args.log_level is None: args.log_level = "INFO"

  return parser, args

def main(argv, stdout, environ):
  if sys.version_info < (3, 0): reload(sys); sys.setdefaultencoding('utf8')

  parser, args = parse_args(argv)

  numeric_loglevel = getattr(logging, args.log_level.upper(), None)
  if not isinstance(numeric_loglevel, int):
    raise ValueError('Invalid log level: %s' % args.log_level)

  logging.basicConfig(format="[%(asctime)s] %(levelname)-8s %(message)s",
                       datefmt="%m/%d %H:%M:%S", level=numeric_loglevel)

  if args.test_flag:  test();   return

  start()

if __name__ == "__main__":
  main(sys.argv, sys.stdout, os.environ)
