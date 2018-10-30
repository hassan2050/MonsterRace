import pygame
import logging

BOARD = 1
OUT = 1
IN = 1
BCM = 1
gpiosurface = None

def setmode(a):
   logging.debug ('GPIO.setmode: %s' % repr(a))
def setup(a, b):
   logging.debug ('GPIO.setup: %s' % repr(a))
def output(a, b):
   logging.debug ('GPIO.output: %s %s' % (a,b))
   p = (a*20,20)
   if (gpiosurface!=None):
       pygame.draw.circle(gpiosurface, (249,8,28), p, 10)
       if (b==0):
          pygame.draw.circle(gpiosurface, (10,10,10), p, 8)
   else:
       logging.debug('no gpio surface')
def cleanup():
   logging.debug ('GPIO.cleanup')
def setwarnings(flag):
   logging.debug ('GPIO.setwarnings: %s' %flag)
def setsurface(surface):
    logging.debug('set surface')
    global gpiosurface
    gpiosurface=surface
