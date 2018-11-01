from PIL import Image

import time
import pygame

import logging

def loadSprite(imagename, frames, startIndex = 0, label=None, offset=1, animation_time=.1):
  images = []
  for frameno in range(frames):
    image_frame_name=imagename+str('{0:02d}'.format(frameno+1))+'.png'
    images.append(pygame.image.load(image_frame_name).convert_alpha())

  return AnimatedSprite(images, startIndex=startIndex, label=label, offset=offset, animation_time=animation_time)

class AnimatedSprite():
  def __init__(self, images, startIndex=0, label=None, offset=1, animation_time=.1):
    logging.debug("AnimatedSprite init: ")
    self.images = images[:]
    self.index = self.startIndex = startIndex
    self.image = self.images[self.startIndex]  # 'image' is the current image of the animation.
    self.animation_time = animation_time
    self.startTime = time.time()
    self.offset = offset

    self.active = True

  def pause(self):
    self.active = False
    
  def run(self):
    self.active = True
    self.startIndex = self.index
    self.startTime = time.time()

  def update(self, screen, x=None,y=None):
    if self.active:
      dt = round((time.time() - self.startTime) / self.animation_time)

      self.index = (dt + self.startIndex) % len(self.images)

    self.image = self.images[self.index]
    screen.blit(self.image, [x,y])
