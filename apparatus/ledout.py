
from enum import Enum
from threading import Semaphore, Thread


COLORS = {
    "BLACK": 0x000000,
    "WHITE": 0xFFFFFF,
    "RED": 0xFF0000,
    "GREEN": 0x00FF00,
    "BLUE": 0x0000FF,
    "ORANGE": 0xFFC000,
    "YELLOW": 0xFFFC00,
    "CYAN": 0x00FFFF,
    "MAGENTA": 0xFF0000,
    "RADICAL_RED": 0xFF355E,
    "WILD_WATERMELON": 0xFD5B78,
    "OUTRAGEOUS_ORANGE": 0xFF6037,
    "ATOMIC_TANGERINE": 0xFF9966,
    "NEON_CARROT": 0xFF9933,
    "SUNGLOW": 0xFFCC33,
    "LASER_LEMON": 0xFFFF66,
    "UNMELLOW_YELLOW": 0xFFFF66,
    "ELECTRIC_LIME": 0xCCFF00,
    "SCREAMIN_GREEN": 0x66FF66,
    "MAGIC_MINT": 0xAAF0D1,
    "BLIZZARD_BLUE": 0x50BFE6,
    "SHOCKING_PINK": 0xFF6EFF,
    "RAZZLE_DAZZLE_ROSE": 0xEE34D2,
    "HOT_MAGENTA": 0xFF00CC,
    "PURPLE_PIZZAZZ": 0xFF00CC
}


class LEDColorCorrection(Enum):
    # Source: https://github.com/FastLED/FastLED/blob/b5874b588ade1d2639925e4e9719fa7d3c9d9e94/src/color.h
    # Color correction starting points
    # RGB
    # --- typical values for SMD5050 LEDs
    # ---@{
    # / * 255, 176, 240 * /,
    TypicalSMD5050 = 0xFFB0F0
    # / * 255, 176, 240 * /,
    TypicalLEDStrip = 0xFFB0F0
    # ---@}

    # --- typical values for 8mm "pixels on a string"
    # --- also for many through-hole 'T' package LEDs
    # ---@{
    # /* 255, 224, 140 */,
    Typical8mmPixel = 0xFFE08C
    # /* 255, 224, 140 */,
    TypicalPixelString = 0xFFE08C
    # ---@}

    # --- uncorrected color
    UncorrectedColor = 0xFFFFFF
    # -----------------------------


class LedOut(object):

    strip = None
    channel: int = 0

    _stripColor: COLORS

    _setColorSemaphore: Semaphore
    _stop_set_thread: bool
    _setThread: Thread
    color_correction: int = 0

    def __init__(self, num_led, mosi, sclk, baud, refresh_rate_s=None):

        # Initialize the library and the strip
        from apa102_pi.driver import apa102

        self.strip = apa102.APA102(num_led=num_led, order='rgb',
                                   bus_speed_hz=baud, mosi=mosi, sclk=sclk)
        self.strip.set_global_brightness(31)
        self._stripColor = COLORS["BLACK"]

        self.refresh_rate_s = refresh_rate_s
        self.color_correction = LEDColorCorrection.UncorrectedColor.value
        self._setColorSemaphore = Semaphore(0)
        self._stop_set_thread = False
        self._setThread = Thread(
            target=self._setThreadMethode, args=(lambda: self._stop_set_thread,), daemon=True)
        self._setThread.start()

    def _setThreadMethode(self, stop):
        while not stop():
            if self._setColorSemaphore.acquire(timeout=self.refresh_rate_s):
                self.setColor()

    def cleanup(self):
        self._stop_set_thread = True
        self.setColor()
        self.strip.cleanup()

    def asyncSetColor(self, value):
        self._stripColor = value
        self._setColorSemaphore.release()

    def setColor(self, value=None):
        if value is not None:
            self._stripColor = value
        NUM_LED = self.strip.num_led

        for led_id in range(0, NUM_LED):
            # Initialise overall color
            self.set_pixel_rgb(
                led_id, self._stripColor, bright_percent=100)

            # Set Signal Light
            if led_id in range(NUM_LED-7, NUM_LED):
                if self.testlight:
                    # Test Light On
                    self.set_pixel_rgb(
                        led_id, self.testlight_color, bright_percent=100)
                else:
                    # Test Light Off
                    # --- Only light single LED
                    if led_id in [NUM_LED-1]:
                        self.set_pixel_rgb(
                            NUM_LED-1, self._stripColor, bright_percent=100)
                    else:
                        self.set_pixel_rgb(
                            led_id, COLORS["BLACK"], bright_percent=100)

            # Set Human Light
            if led_id in range(20, 30):
                if self.humanlight:
                    # Light On
                    self.set_pixel_rgb(
                        led_id, self.humanlight_color, bright_percent=100)
                else:
                    # Light Off
                    self.set_pixel_rgb(
                        led_id, COLORS["BLACK"], bright_percent=100)

        self.strip.show()

    def set_pixel_rgb(self, led_num, rgb_color, bright_percent=100):
        self.strip.set_pixel_rgb(
            led_num,
            self.colorCorrection(rgb_color),
            bright_percent
        )

    def setColorCorrection(self, value):
        self.color_correction = value

    def colorCorrection(self, value):
        # GetBytes
        CRed = (value >> 16) & 0xFF
        CGreen = (value >> 8) & 0xFF
        CBlue = (value >> 0) & 0xFF
        # GetScales
        SRed = (self.color_correction >> 16) & 0xFF
        SGreen = (self.color_correction >> 8) & 0xFF
        SBlue = (self.color_correction >> 0) & 0xFF
        # CorrectValues
        Red = int((CRed * SRed) / 0xFF)
        Green = int((CGreen * SGreen) / 0xFF)
        Blue = int((CBlue * SBlue) / 0xFF)
        # CombineBytes
        return Red << 16 | Green << 8 | Blue << 0

    _testlight = False

    @property
    def testlight(self):
        """I'm the 'x' property."""
        return self._testlight

    @testlight.setter
    def testlight(self, value):
        self._testlight = value
        self.asyncSetColor(self._stripColor)

    _testlight_color = COLORS["RED"]

    @property
    def testlight_color(self):
        """I'm the 'x' property."""
        return self._testlight_color

    @testlight_color.setter
    def testlight_color(self, value):
        self._testlight_color = value
        self.asyncSetColor(self._stripColor)

    _humanlight = False

    @property
    def humanlight(self):
        """I'm the 'x' property."""
        return self._humanlight

    @humanlight.setter
    def humanlight(self, value):
        self._humanlight = value
        self.asyncSetColor(self._stripColor)

    _humanlight_color = COLORS["RED"]

    @property
    def humanlight_color(self):
        """I'm the 'x' property."""
        return self._humanlight_color

    @humanlight_color.setter
    def humanlight_color(self, value):
        self._humanlight_color = value
        self.asyncSetColor(self._stripColor)
