import logging
import time

from apparatus.apparatus_config import config
from apparatus.apparatus_interface import ApparatusInterface
from apparatus.carousel import Carousel
from apparatus.ledout import COLORS, LedOut
from apparatus.lever import Lever


class Apparatus(ApparatusInterface):
    """ Class to control a Apparatus """

    carousel = (None, None)
    wait_callback = None
   # ledout: LedOut = None

    def __init__(self):
        """ class init
        """
        self.carousel1 = Carousel(
            config.carousel1['stepper_step'],
            config.carousel1['stepper_dir'],
            config.carousel1['stepper_en'],
            config.carousel1['as5048b_address'],
            config.carousel1['as5048b_zeroreg'],
            config.carousel1['monkey_door_id'],
            config.carousel1['monkey_door_range'],
            config.carousel1['human_door_id'],
            config.carousel1['human_door_range'],
            config.carousel1['servo_timeout'],
            config.carousel1['nema_timeout'],
            config.carousel1['sensorless'],
        )

        self.carousel2 = Carousel(
            config.carousel2['stepper_step'],
            config.carousel2['stepper_dir'],
            config.carousel2['stepper_en'],
            config.carousel2['as5048b_address'],
            config.carousel2['as5048b_zeroreg'],
            config.carousel2['monkey_door_id'],
            config.carousel2['monkey_door_range'],
            config.carousel2['human_door_id'],
            config.carousel2['human_door_range'],
            config.carousel2['servo_timeout'],
            config.carousel2['nema_timeout'],
            config.carousel2['sensorless'],
        )

        NUM_LED = config.led_strip['count']
        # Hardware SPI uses BCM 10 & 11. Change these values for bit bang mode
        MOSI = config.led_strip['mosi']
        # e.g. MOSI = 23, SCLK = 24 for Pimoroni Phat Beat or Blinkt!
        SCLK = config.led_strip['sclk']
        # levelshifter BAUD (3.3-Vto 5-V Translation)
        SN74LVC2T45_MAXBAUD = config.led_strip['baud']

        self.ledout = LedOut(NUM_LED, MOSI, SCLK,
                             SN74LVC2T45_MAXBAUD, refresh_rate_s=1/20)

        self.lever = Lever(
            config.lever['switch_io'],
            config.lever['touch_io'],
            config.lever['switch_up_io'],
            config.lever['lock_servo_id'],
            config.lever['lock_servo_range'],
            config.lever['servo_timeout'],
            self._io_callback,
        )

        # self.pcb_led = Servo(config.pcb_led['led_servo_id'], config.pcb_led['led_servo_range'])
        # self.pcb_led.lever_open = True

        self.carousel = (self.carousel1, self.carousel2)

    def set_io_callback(self, callback):
        self.lever.io_callback = callback

    def set_wait_callback(self, callback):
        self.wait_callback = callback

    def _io_callback(self, pin_io, name, state):
        logging.debug("GOT IO")
        pass

    def _wait_callback(self, carousel_id, func_name):
        logging.debug("wait callback: %s" % func_name)
        if self.wait_callback is not None:
            self.wait_callback(carousel_id, func_name)

    def cleanup(self):
        # self.pcb_led.lever_open = False
        # self.pcb_led.cleanup()
        # self.lever.cleanup(gpio=False)
        self.ledout.cleanup()
        self.carousel[0].cleanup()
        self.carousel[1].cleanup()
        # clean up gpio last
        # GPIO.cleanup()

    def motors_off(self):
        self.carousel[0].motors_off()
        self.carousel[1].motors_off()

    def init_hw(self):
        logging.info("Initialise LED")
        self.ledout.asyncSetColor(COLORS['BLACK'])
        self.ledout.humanlight_color = COLORS['ELECTRIC_LIME']
        self.ledout.humanlight = True
        self.ledout.testlight = False

        logging.info("Initialise Carousel 1")
        self.carousel1.servo_human.door_open = False
        self.carousel1.servo_monkey.door_open = False
        self.carousel1.move_to(0, monkey=True, blocking=False)

        logging.info("Initialise Carousel 2")
        self.carousel2.servo_human.door_open = False
        self.carousel2.servo_monkey.door_open = False
        self.carousel2.move_to(0, monkey=True, blocking=False)
        self.carousel1.move_to_wait()

        logging.info("Wait for Carousel 1 to reach target")
        self.carousel2.move_to_wait()

        logging.info("Initialise Lever")
        self.lever.lever_open = False

        # "precache sounds"
        import os
        soundfiles = [os.path.join(config.apparatus['sounds_path'], f) for f in os.listdir(
            config.apparatus['sounds_path'],) if os.path.isfile(os.path.join(config.apparatus['sounds_path'], f))]
        for f in soundfiles:
            self.play_sound(f, volume=0)

    def hw_self_test(self):
        logging.debug(self._localtodict(locals()))
        pass

    def play_sound(self, file="on-status.mp3", volume=90, timestamp=None):
        import os
        import subprocess

        file = os.path.join(config.apparatus['sounds_path'], file)

        FNULL = open(os.devnull, 'w')

        p = subprocess.Popen(["amixer", "--c", "0", "set", "Headphone", "playback", str(volume)+"%", "unute"],
                             stdout=FNULL,
                             stderr=subprocess.STDOUT)
        p = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", file],
                             stdout=FNULL,
                             stderr=subprocess.STDOUT)

    def empty_human(self):
        self.carousel1.servo_human.door_open = True
        self.carousel2.servo_human.door_open = True
        time.sleep(2)
        for compartment in range(0, 16+4, 4):
            self.carousel1.move_to(
                compartment, monkey=False, blocking=False)
            self.carousel2.move_to(
                compartment, monkey=False, blocking=False)
            self.carousel1.move_to_wait()
            self.carousel2.move_to_wait()
        time.sleep(2)
        self.carousel2.servo_human.door_open = False
        self.carousel1.servo_human.door_open = False

        pass

    def move_to(self, carousel_id, compartment_id, monkey=False, blocking=False):
        self.carousel[carousel_id].move_to(compartment_id,
                                           monkey,
                                           callback=lambda: self._wait_callback(carousel_id, "move_to"))
        pass

    def move_to_wait(self, carousel_id):
        logging.warn("move_to_wait not implemented")

    def deploy(self, carousel_id, compartment_id, monkey=False, blocking=False):
        self.carousel[carousel_id].deploy(compartment_id,
                                          monkey,
                                          callback=lambda: self._wait_callback(carousel_id, "move_to"))

    def deploy_wait(self, carousel_id):
        logging.warn("deploy_wait not implemented")

    def set_test_light(self, state, color=None, timestamp=None):
        if color is not None:
            self.ledout.testlight_color = color
        self.ledout.testlight = state
        pass

    def set_human_light(self, state, color=None):
        if color is not None:
            self.ledout.humanlight_color = color
        self.ledout.humanlight = state
        pass

    def set_light(self, color, timestamp=None):
        self.ledout.asyncSetColor(color)
        pass

    def wait_lever_state(self, pin_io, state, timeout=-1, spinlock=False) -> bool:
        logging.warn("wait_lever_state not implemented")
        return True

    def set_lever_open(self, state, timestamp=None):
        self.lever.lever_open = state
        pass
