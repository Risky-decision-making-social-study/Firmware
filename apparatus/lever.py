import logging
import threading
import time
from contextlib import contextmanager

import RPi.GPIO as GPIO

from apparatus.apparatus_config import config
from apparatus.servo import Servo


class ButtonHandler():
    def __init__(self, pin, func, edge='both', bouncetime=50):
        GPIO.setup(pin, GPIO.IN)
        self.edge = edge
        self.func = func
        self.pin = pin
        self.bouncetime = float(bouncetime)/1000

        self.lastpinval = GPIO.input(self.pin)
        self.lock = threading.Lock()

        gpioedge = GPIO.BOTH

        if edge == "falling":
            gpioedge = GPIO.FALLING
        elif edge == "rising":
            gpioedge = GPIO.RISING

        GPIO.add_event_detect(pin, gpioedge, callback=self.call)

    def call(self, *args):
        if not self.lock.acquire(blocking=False):
            return

        t = threading.Timer(self.bouncetime, self.read, args=args)
        t.start()

    def read(self, *args):
        pinval = GPIO.input(self.pin)

        if (
                ((pinval == 0 and self.lastpinval == 1) and
                 (self.edge in ['falling', 'both'])) or
                ((pinval == 1 and self.lastpinval == 0) and
                 (self.edge in ['rising', 'both']))
        ):
            self.func(*args)

        self.lastpinval = pinval
        self.lock.release()


class Lever(object):
    """ Class to control a Apparatus """

    channel = 0

    switch_io = 0
    switch_io_lock = None
    switch_io_lock_target_state = None
    switch_io_handler = None

    touch_io = 0
    touch_io_lock = None
    touch_io_lock_target_state = None
    touch_io_handler = None

    switch_up_io = 0
    switch_up_io_lock = None
    switch_up_io_lock_target_state = None
    switch_up_io_handler = None

    def __init__(self, switch_io, touch_io, switch_up_io, servo_id=0, servo_range=(0, 1), servo_timeout=0, io_callback=None):
        """ class init
        """
        self.switch_io = switch_io
        self.touch_io = touch_io
        self.switch_up_io = switch_up_io
        self.channel = servo_id

        self.switch_io_lock = threading.Lock()
        self.touch_io_lock = threading.Lock()

        self.servo = Servo(self.channel, servo_range, servo_timeout)

        self.io_callback = io_callback

        self.switch_io_handler = ButtonHandler(switch_io, lambda x: self.io_handler(
            switch_io, "LEVER_SWITCH_IO"), bouncetime=config.lever["switch_io_bounce_time"])

        self.touch_io_handler = ButtonHandler(touch_io, lambda x: self.io_handler(
            touch_io, "LEVER_TOUCHS_IO"), bouncetime=config.lever["touch_io_bounce_time"])

        self.touch_io_handler = ButtonHandler(switch_up_io, lambda x: self.io_handler(
            switch_up_io, "LEVER_SWITCH_UP_IO"), bouncetime=config.lever["switch_up_io_bounce_time"])

    @property
    def lever_open(self):
        return self.servo.lever_open

    @lever_open.setter
    def lever_open(self, value):
        self.servo.lever_open = value

    @contextmanager
    def _acquire_timeout(self, lock, timeout):
        result = lock.acquire(timeout=timeout)
        yield result
        if not result:
            lock.release()

    def cleanup(self, gpio=True):
        # if gpio:
        # GPIO.cleanup()
        pass

    def wait_lever_state(self, pin_io, state, timeout=-1, spinlock=False):
        if GPIO.input(pin_io) == state:
            return True
        elif pin_io == self.switch_io:
            lock = self.switch_io_lock
            logging.debug("arm lock switch")
            lock.acquire(0)  # arm lock
            logging.debug("Enable release on switch")
            self.switch_io_lock_target_state = state  # Enable release on switch
        elif pin_io == self.touch_io:
            lock = self.touch_io_lock
            logging.debug("arm lock touch")
            lock.acquire(0)  # arm lock
            logging.debug("Enable release on touch")
            self.touch_io_lock_target_state = state  # Enable release on touch
        elif pin_io == self.switch_up_io:
            lock = self.switch_up_io_lock
            logging.debug("arm lock switch")
            lock.acquire(0)  # arm lock
            logging.debug("Enable release on switch_up")
            self.switch_up_io_lock_target_state = state  # Enable release on switch
        else:
            logging.error("pin_io not known!")
            return False

        if spinlock:
            # Spinlock
            timeout = time.time() + timeout   # timeout seconds from now
            while lock.locked():
                if time.time() > timeout:
                    logging.debug("timeout")
                    return False
                time.sleep(0.01)
            logging.debug("state reached")
            return True
        else:
            # Lock sleep
            with self._acquire_timeout(lock, timeout) as acquired:  # wait timeout
                if acquired:
                    logging.debug("state reached")
                    return True
                else:
                    logging.info("timeout")
                    return False

    def io_handler(self, pin_io, name):
        state = GPIO.input(pin_io)
        if pin_io == self.switch_io and self.switch_io_lock_target_state is not None and self.switch_io_lock_target_state == state:
            self.switch_io_lock_target_state = None  # Disable release on switch
            logging.debug("release lock switch")
            self.switch_io_lock.release()
        if pin_io == self.touch_io and self.touch_io_lock_target_state is not None and self.touch_io_lock_target_state == state:
            self.touch_io_lock_target_state = None  # Disable release on touch
            logging.debug("release lock touch")
            self.touch_io_lock.release()
        if pin_io == self.switch_up_io and self.switch_up_io_lock_target_state is not None and self.switch_up_io_lock_target_state == state:
            self.switch_up_io_lock_target_state = None  # Disable release on switch
            logging.debug("release lock switch")
            self.switch_up_io_lock.release()
        # callback
        if self.io_callback:
            self.io_callback(pin_io, name, state)
        if state:
            logging.info(name+' HIGH!')
        else:
            logging.info(name+' LOW!')

    def get_switch_io_state(self):
        return GPIO.input(self.switch_io)

    def get_touch_io_state(self):
        return GPIO.input(self.touch_io)

    def get_switch_up_io_state(self):
        return GPIO.input(self.switch_up_io)
