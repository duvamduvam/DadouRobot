#linux rpi install : sudo pip3 install Adafruit-Blinka
#sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
# sudo python3 -m pip install --force-reinstall adafruit-blinka
# sudo pip3 install adafruit-circuitpython-led-animation
import random
import time
import board
import neopixel
import logging.config
from rainbowio import colorwheel
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.colorcycle import ColorCycle
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation.sparklepulse import SparklePulse
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.color import WHITE, MAGENTA, ORANGE, TEAL, JADE, PURPLE, AMBER
import adafruit_fancyled.adafruit_fancyled as fancy


#todo check thread : https://www.geeksforgeeks.org/python-communicating-between-threads-set-1/
#todo check thread2 : https://riptutorial.com/python/example/4691/communicating-between-threads

class Lights:

    logging.config.fileConfig(fname='logging.conf', disable_existing_loggers=False)

    RED = (255, 0, 0)
    YELLOW = (255, 150, 0)
    GREEN = (0, 255, 0)
    CYAN = (0, 255, 255)
    BLUE = (0, 0, 255)
    PURPLE = (180, 0, 255)
    BLACK = (0, 0, 0)

    # LED strip configuration:
    LED_COUNT = 250  # Number of LED pixels.
    LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
    # LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
    LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA = 10  # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 0  # Set to 0 for darkest and 255 for brightest
    LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53

    strip = neopixel.NeoPixel(board.D18, LED_COUNT)
    strip.brightness = 0.1

    #strip = neopixel.NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    # strip.begin()

    # F Turns the NeoPixels red, green, and blue in sequence.
    #TODO check examples : https://www.digikey.fr/en/maker/projects/circuitpython-led-animations/d15c769c6f6d411297657c35f0166958

    current_animation = {}

    def chase(self):
        chase = Chase(self.strip, speed=0.1, color=WHITE, size=3, spacing=6)
        while True:
            chase.animate()

    def blink(self):
        blink = Blink(self.strip, speed=0.5, color=JADE)
        while True:
            blink.animate()

    def color_cycle(self):
        colorcycle = ColorCycle(self.strip, 0.5, colors=[MAGENTA, ORANGE, TEAL])
        while True:
            colorcycle.animate()

    def comet(self):
        comet = Comet(self.pixels, speed=0.01, color=PURPLE, tail_length=10, bounce=True)
        while True:
            comet.animate()

    def pulse(self):
        pulse = Pulse(self.strip, speed=0.1, color=AMBER, period=3)
        while True:
            pulse.animate()

    def rainbow(self):
        rainbow = Rainbow(self.strip, speed=0.1, period=2)
        while True:
            rainbow.animate()

    def rainbow_chase(self):
        rainbow_chase = RainbowChase(self.strip, speed=0.1, size=5, spacing=3)
        while True:
            rainbow_chase.animate()

    def rainbow_comet(self):
        rainbow_comet = RainbowComet(self.strip, speed=0.1, tail_length=7, bounce=True)
        while True:
            rainbow_comet.animate()

    def rainbow_sparkle(self):
        rainbow_sparkle = RainbowSparkle(self.strip, speed=0.1, num_sparkles=15)
        while True:
            rainbow_sparkle.animate()

    def sparkle(self):
        sparkle = Sparkle(self.strip, speed=0.05, color=AMBER, num_sparkles=10)
        while True:
            sparkle.animate()

    def sparkle_pulse(self):
        sparkle_pulse = SparklePulse(self.strip, speed=0.05, period=3, color=JADE)
        while True:
            sparkle_pulse.animate()

    def fade_red(self):
        self.strip.fill((255, 0, 0))
        time.sleep(0.5)
        self.strip.fill((0, 255, 0))
        time.sleep(0.5)
        self.strip.fill((0, 0, 255))
        time.sleep(0.5)

    def random(self):
        #red = 0x100000
        i = random.randint(0, self.LED_COUNT)
        blue = random.randint(0, 255)
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        self.strip[i] = (blue, red, green)

    def fill(self, color):
        logging.info("fill strip with "+str(color))
        self.strip.fill(color)

    def clean(self):
        self.strip.fill(self.BLACK)

    def color_chase(self, color, wait):
        for i in range(self.LED_COUNT):
            self.strip[i] = color
            time.sleep(wait)
            self.strip.show()
        time.sleep(0.5)

    def rainbow_cycle(self, wait):
        for j in range(255):
            for i in range(self.LED_COUNT):
                rc_index = (i * 256 // self.LED_COUNT) + j
                self.strip[i] = colorwheel(rc_index & 255)
            self.strip.show()
            time.sleep(wait)

    def animate(self):
        self.current_animation.animate()

    def animate_loop(self, time):
        #todo animate with time
        self.current_animation.animate()