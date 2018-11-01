import time
import logging

class BlinkingLED():

  def __init__(self, GPIO, leftpin, rightpin, animation_time=0.1):
    logging.debug("BlinkingLED init ")
    self.leds = [leftpin, rightpin]
    self.index = 0
    self.leftpin = leftpin
    self.rightpin = rightpin
    self.GPIO = GPIO
    self.animation_time = animation_time
    self.startTime = time.time()

  def update(self):
    current_time = time.time() - self.startTime
    if current_time >= self.animation_time:
      self.startTime = time.time()
      on = self.index % 2
      off = on ^ 1 

      self.GPIO.output(self.leds[on], 1)
      self.GPIO.output(self.leds[off], 0)

      self.index += 1
