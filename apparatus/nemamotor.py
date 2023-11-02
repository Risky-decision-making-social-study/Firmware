# Import the system modules needed to run mokey_motors.stepper
import logging
import math
import sys
import threading
import time

import RPi.GPIO as GPIO


class NemaMotor(object):
    """ Class to control a Nema bi-polar stepper motor with a TMC2209 """

    _timer: threading.Timer = None
    _nema_timeout: float = 0

    def __init__(self, direction_pin, step_pin, enable_pin, mode_pins=None, spread_pin=None, motor_type="TMC2209", nema_timeout=0):
        """ class init method 3 inputs
        (1) direction type=int , help=GPIO pin connected to DIR pin of IC
        (2) step_pin type=int , help=GPIO pin connected to STEP of IC
        (3) mode_pins type=tuple of 2 ints, help=GPIO pins connected to
        Microstep Resolution pins MS1-MS2 of IC
        (4) motor_type type=string, help=TYpe of motor two options: TMC2209 or DRV8825
        """
        self.motor_type = motor_type
        self.direction_pin = direction_pin
        self.step_pin = step_pin
        self.enable_pin = enable_pin
        self.mode_pins = mode_pins
        self.spread_pin = spread_pin

        self._nema_timeout = nema_timeout

        self.running = threading.Lock()

        GPIO.setwarnings(False)

    def cleanup(self):
        self.motor_enable(False)
        # GPIO.cleanup()

    def resolution_set(self, steptype):
        """ method to calculate step resolution
        based on motor type and steptype"""
        if self.motor_type == "TMC2209":
            resolution = {'1/8': (0, 0),
                          '1/32': (0, 1),
                          '1/64': (1, 0),
                          '1/16': (1, 1)}
        else:
            logging.error("invalid motor_type: {}".format(self.motor_type))
            quit()

        # error check stepmode
        if steptype in resolution:
            pass
        else:
            logging.error("invalid steptype: {}".format(steptype))
            quit()
        if self.mode_pins:
            GPIO.output(self.mode_pins, resolution[steptype])

    def motor_enable(self, enable=True):
        GPIO.setup(self.enable_pin, GPIO.OUT)
        GPIO.output(self.enable_pin,
                    GPIO.LOW if enable else GPIO.HIGH)  # Enable

    def motor_step(self, steps, step=0, state=False):
        if step == 0:
            self.running.acquire()
        if state:
            state = False
        else:
            step += 1
            state = True

        GPIO.setmode(GPIO.BCM)

        GPIO.output(self.step_pin, state)

        if step < steps:
            threading.Timer(self.motor_times(step, steps),
                            self.motor_step, args=[steps, step, state]).start()
        else:
            self.running.release()

    def wait_finished(self):
        self.running.acquire()
        self.running.release()  # Wait till its over

    def running(self):
        self.running.lo

    def motor_go(self, clockwise=False, steptype="1/8",
                 steps=200, stepdelay=.001, verbose=False, initdelay=.05):
        """ motor_go,  moves stepper motor based on 6 inputs

         (1) clockwise, type=bool default=False
         help="Turn stepper counterclockwise"
         (2) steptype, type=string , default=Full help= type of drive to
         step motor 4 options
            (00: 1/8, 01: 1/32, 10: 1/64 11: 1/16)
         (3) steps, type=int, default=200, help=Number of steps sequence's
         to execute. Default is one revolution , 200 in Full mode.
         (4) stepdelay, type=float, default=0.05, help=Time to wait
         (in seconds) between steps.
         (5) verbose, type=bool  type=bool default=False
         help="Write pin actions",
         (6) initdelay, type=float, default=1mS, help= Intial delay after
         GPIO pins initialized but before motor is moved.

        """
        if steps < 0:
            steps = -steps
            clockwise = not clockwise

        # setup GPIO
        self.motor_enable()
        GPIO.setup(self.direction_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)

        GPIO.output(self.direction_pin, clockwise)
        if self.mode_pins:
            GPIO.setup(self.mode_pins, GPIO.OUT)

        try:
            # dict resolution
            self.resolution_set(steptype)
            time.sleep(initdelay)

            self.motor_step(steps)

            self.wait_finished()

        except KeyboardInterrupt:
            logging.error("User Keyboard Interrupt : mokey_motors.stepper:")
        except Exception as motor_error:
            logging.error(sys.exc_info()[0])
            logging.error(motor_error)
            logging.error("mokey_motors.stepper  : Unexpected error:")
        else:
            # print report status
            if verbose:
                logging.error(
                    "\nmokey_motors.stepper, Motor Run finished, Details:.\n")
                logging.error("Motor type = {}".format(self.motor_type))
                logging.error("Clockwise = {}".format(clockwise))
                logging.error("Step Type = {}".format(steptype))
                logging.error("Number of steps = {}".format(steps))
                logging.error("Step Delay = {}".format(stepdelay))
                logging.error("Intial delay = {}".format(initdelay))
                logging.error("Size of turn in degrees = %d @ %s" %
                              (steps, steptype))
        finally:
            # cleanup
            GPIO.output(self.step_pin, False)
            GPIO.output(self.direction_pin, False)
            GPIO.output(self.enable_pin, False)
            if self.mode_pins:
                for pin in self.mode_pins:
                    GPIO.output(pin, False)
        self._startTimeout()

    # import math
    # [sigmoid(x) for x in range(-10,10)]
    def sigmoid(self, x, c_1, c_2, max, min):
        return ((max - min) / (1 + math.exp(-c_1 * (x - c_2)))) + min

    def motor_times(self, step, steps):
        c_1 = 0.2
        c_2 = 20
        max = 0.00120
        min = 0.00060
        x = 0

        if(step <= steps / 2):
            x = step
        else:
            x = steps - step - 1

        return max + min - self.sigmoid(x, c_1, c_2, max, min)

    # [motor_times(x, 50) for x in range(0, 50)]

    def _startTimeout(self):
        if self._nema_timeout <= 0:
            return
        if self._timer is not None:
            self._timer.cancel()
        # Disable Servo after "_servo_timeout" sec.
        self._timer = threading.Timer(
            interval=self._nema_timeout,
            function=self.motor_enable,
            args=(False,),
        )
        self._timer.start()
