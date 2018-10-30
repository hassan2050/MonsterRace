import logging

class BlinkingLED():

    def __init__(self, GPIO,leftpin,rightpin,animation_time=0.1):
        """
        BlinkingLED

        Args:
            position: leftpin, rightpin of GPIO to turn on/off
            images: Images to use in the animation.
        """
        logging.debug("BlinkingLED init ")
        self.leds=[leftpin, rightpin]
        self.index=0
        self.leftpin= leftpin
        self.rightpin= rightpin
        self.GPIO= GPIO
        self.animation_time = animation_time
        self.current_time = 0

    def update(self, dt):
        """
        Updates the Blinking LED

        Args:
            dt: Time elapsed between each frame.
        """
        self.current_time += dt
        if self.current_time >= self.animation_time:
            self.current_time = 0
            on=self.index%2
            if (on==0):
               off=1
            else:
               off=0
            self.GPIO.output(self.leds[on],1)
            self.GPIO.output(self.leds[off],0)
            self.index=self.index+1
