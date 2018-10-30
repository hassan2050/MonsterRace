import time
import logging

def dispense_init():
    logging.debug("Initializing servo")
def dispense_back(channel = None):
    logging.debug("Dispenser " + str(channel+1)+": Pulling Back")
def dispense_forward(channel = None):
    logging.debug("Dispenser " + str(channel+1)+": Dispensing Candy")

