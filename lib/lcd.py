from reactor import Reactor
from Adafruit_CharLCD import Adafruit_CharLCD as CharLCD
import time
from threading import Thread

class LCDReactor(Reactor):
    event_kinds = {"input"}

    def react(self, alert):
        LCDReactor.Display(alert.extra).start()

    class Display(Thread):
        # TODO: move this to a config file
        COLS = 16
        ROWS = 2
        COL_OFFSET = 2 # You may choose to add an offset to the original position
        DURATION = 15
        PREFIX = "WARNING: "
        START_POSITION = Display.COLS - Display.COL_OFFSET

        def __init__(self, msg):
            Thread.__init__(self)
            self.msgs = [Display.PREFIX, msg]
            self.lcd = CharLCD(pin_rs=2, pin_e=4, pins_db=[3, 14, 25, 24])

        def init_display(self):
            self.lcd.clear()
            self.lcd.begin(Display.COLS, Display.ROWS)

        def display_message(self):
            self.lcd.setCursor(Display.START_POSITION, 0)
            self.lcd.message(self.msgs[0])
            self.setCursor(Display.START_POSITION, 1)
            self.lcd.message(self.msgs[1])

        def shift_text(self):
            self.lcd.DisplayLeft()
            time.sleep(0.3)

        def loop_message(self):
            # Calculate the maximum length and the start position
            # Needed for when the time runs out and the message is in the
            # middle of the LCD
            position = Display.START_POSITION
            max_len = max(len(self.msgs[0], self.msgs[1]))
            start_time = time.time()

            # Display for n seconds
            while time.time() < start_time + Display.DURATION:
                self.shift_text()
                position = (position + 1) % max_len

            # If the text is in the middle of the screen, we want to shift it
            # off. The best way is to take the current position and move it
            # until the the position is out of the display.
            # "Out of display" is given by max_len (maximum image size) +
            # START_POSITION, since it starts in the right side of the LCD
            for x in range(position, Display.START_POSITION + max_len):
                self.shift_text()

            self.lcd.clear()


        def display(self):
            self.init_display()
            self.display_message()
            self.loop_message()

        def run(self):
            self.display()

