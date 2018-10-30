# Simple demo of of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 from min to max position repeatedly.
# Author: Tony DiCola
# License: Public Domain
from __future__ import division
import time
try:
  import config
except ImportError:
    print ("no config.py found.  Please copy sample_config.py to config.py.")

# Import the PCA9685 module.
import Adafruit_PCA9685


# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).


# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Set frequency to 60hz, good for servos.
pwm = Adafruit_PCA9685.PCA9685()
def dispense_init():
    pwm.set_pwm_freq(60)
    pwm.set_pwm(0, 0, config.servo_min)
    pwm.set_pwm(1, 0, config.servo_min)
    pwm.set_pwm(2, 0, config.servo_min)
    pwm.set_pwm(3, 0, config.servo_min)
    logging.debug("Initializing servo")
def dispense_back(channel):
    # Move servo on channel O between extremes.
    pwm.set_pwm(channel, 0, config.servo_max)
    logging.debug("Dispenser " + str(channel+1)+": Pulling Back")
def dispense_forward(channel):
    pwm.set_pwm(channel, 0, config.servo_min)
    logging.debug("Dispenser " + str(channel+1)+": Dispensing Candy")

if __name__ == "__main__":
    for i in range(42):
        dispense_back(0)
        dispense_back(1)
        dispense_back(2)
        dispense_back(3)
        time.sleep(2)
        dispense_forward(0)
        dispense_forward(1)
        dispense_forward(2)
        dispense_forward(3)
        time.sleep(2)
