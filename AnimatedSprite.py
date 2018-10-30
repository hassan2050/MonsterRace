from PIL import Image
import pygame

import logging

def loadSprite(imagename, frames, index = 0, label=None,offset=1,animation_time=.1):
  images = []
  for frameno in range(frames):
       image_frame_name=imagename+str('{0:02d}'.format(frameno+1))+'.png'
       images.append(pygame.image.load(image_frame_name).convert_alpha())

  return AnimatedSprite(images, index=index, label=label, offset=offset, animation_time=animation_time)

class AnimatedSprite():
    def __init__(self, images, index = 0, label=None,offset=1,animation_time=.1):
        """
        Animated sprite object.

        Args:
            position: x, y coordinate on the screen to place the AnimatedSprite.
            images: Images to use in the animation.
        """
        logging.debug("AnimatedSprite init: ")
        self.images = images[:]
        self.index = index
        self.image = self.images[self.index]  # 'image' is the current image of the animation.
        self.animation_time = animation_time
        self.current_time = 0
        self.offset=offset

        self.current_frame = 0
        self.label = label
        #self.label = pygame.image.load('images/endgame.png').convert_alpha()
        if self.label:
            self.label_rect = self.label.get_rect()
    def update(self, dt, screen, x=None,y=None):
        """
        Updates the image of Sprite approximately every 0.1 second.

        Args:
            dt: Time elapsed between each frame.
        """
        #width = screen.get_width()
        #height = screen.get_height()
        width = 512 
        height = 128 

        self.current_time += dt
        if self.current_time >= self.animation_time:
            self.current_time = 0
            self.index = (self.index + self.offset) % len(self.images)
            self.image = self.images[self.index]
        self.image_rect = self.image.get_rect()
        if not x and not self.label:
            self.image_rect.center = (width/2, height/2)
            screen.blit(self.image, self.image_rect)
        elif not self.label:
            screen.blit(self.image, [x,y])
        if self.label:
            self.image_rect.center = (width - (width/8), height/2) #should be calculated later
            screen.blit(self.image, self.image_rect)
            self.label_rect.center = (width/2,height/2)
            screen.blit(self.label, self.label_rect)
