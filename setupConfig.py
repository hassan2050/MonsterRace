#! /usr/bin/env python3

"""python program to solve the world problems..."""

import os, sys, string, time, logging, argparse
import json

_version = "0.1"

import RPi.GPIO as GPIO

import dispense
import pygame


#leds = [ (24,25),(22,23),(20,21),(19,18)]
leds = range(18,26)

def setup():
  pygame.init()
  screen = pygame.display.set_mode((640,480))

  ## joystick
  pygame.joystick.init()
  joystick_count = pygame.joystick.get_count()
  for i in range(joystick_count):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()

  ## lights
  GPIO.setmode(GPIO.BCM)
  for io in leds:
    GPIO.setup(io,GPIO.OUT)

  dispense.dispense_init()

def getButtonPress():
  done = False
  while not done:
    event = pygame.event.wait()
    if event.type == pygame.JOYBUTTONDOWN:
      return (event.dict['button'])

def getButtonRelease():
  done = False
  while not done:
    event = pygame.event.wait()
    if event.type == pygame.JOYBUTTONUP:
      return (event.dict['button'])

def start():
  setup()

  for i in range(8):
    GPIO.output(leds[i],0)

  buttonMap = []
  if 1:
    print("Please press the buttons from left to right when instructed.")
    for i in range(8):
      print("Press button %d." % i, end="", flush=True)
      button = getButtonPress()
      getButtonRelease()
      print ("done")

      buttonMap.append(button)

    print (buttonMap)
    ibuttonMap = {}
    for i,button in enumerate(buttonMap):
      ibuttonMap[button] = i

  ledMap = []

  if 1:
    print("Please press the button that is lit up when instructed.")

    for i in range(8):
      GPIO.output(leds[i],1)
      rawbutton = getButtonPress()
      GPIO.output(leds[i],0)
      getButtonRelease()

      button = ibuttonMap[rawbutton]
      ledMap.append(button)

    iledMap = {}
    for i,button in enumerate(ledMap):
      iledMap[button] = i

    print (ledMap)


  if 1:
    servoMap = []

    for i in range(4):
      dispense.dispense_back(i)
      time.sleep(2)
      dispense.dispense_forward(i)
      time.sleep(2)

      rawbutton = getButtonPress()
      button = ibuttonMap[rawbutton]

      station = button // 2
      print ("station %d" % station)

      servoMap.append(station)

    iservoMap = {}
    for i,station in enumerate(servoMap):
      iservoMap[station] = i

    print (servoMap)

  controls = {}
  controls['servoMap'] = servoMap
  controls['buttonMap'] = buttonMap
  controls['ledMap'] = ledMap

  fp = open("control_config.json", "w")
  json.dump(controls, fp, indent=4)
  fp.close()

  if 1:
    print("Please press any button.")
    done = False
    while not done:
      rawbutton = getButtonPress()
      button = ibuttonMap[rawbutton]
      station = button // 2
      servo = iservoMap.get(station)
      if servo is not None:
        dispense.dispense_back(servo)
      print ("button %d -> station %d" % (button, station))

      led = iledMap[button]

      GPIO.output(leds[led],1)
      
      button = getButtonRelease()
      GPIO.output(leds[led],0)

      if servo is not None:
        dispense.dispense_forward(servo)


def test():
  logging.warn("Testing")

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

  return parser, args

def main(argv, stdout, environ):
  if sys.version_info < (3, 0): reload(sys); sys.setdefaultencoding('utf8')

  parser, args = parse_args(argv)

  logging.basicConfig(format="[%(asctime)s] %(levelname)-8s %(message)s", 
                    datefmt="%m/%d %H:%M:%S", level=args.log_level)

  if args.test_flag:  test();   return

  start()

if __name__ == "__main__":
  main(sys.argv, sys.stdout, os.environ)
