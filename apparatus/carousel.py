import logging
import threading
import time

from apparatus.as5048b import AS5048B
from apparatus.nemamotor import NemaMotor
from apparatus.servo import Servo


class Carousel(object):
    """ Class to control a Apparatus """

    motor: NemaMotor = None
    # encoder: AS5048B = None

    MICROSTEPS = 8
    ANGLE_RES_STEPS = 0.5/MICROSTEPS
    COMPARTMENTS = 16
    STEPS_COMPARTMENT = 360/ANGLE_RES_STEPS
    ANGLE_COMPARTMENT = 360/COMPARTMENTS

    step_pin = 0
    dir_pin = 0
    en_pin = 0
    sensor_addr = 0
    _sensor_zeroreg = 0

    _lock: threading.Lock = None
    _thread: threading.Thread = None

    @property
    def sensor_zeroreg(self):
        """I'm the 'x' property."""
        return self._sensor_zeroreg

    @sensor_zeroreg.setter
    def sensor_zeroreg(self, value):
        self._sensor_zeroreg = value
        if not self.sensorless:
            self.encoder.zeroRegW(value)

    def __init__(self, step_pin, dir_pin, en_pin, sensor_addr=0x40, sensor_zeroreg=0, servo_monkey_id=0, servo_monkey_id_range=(0, 1), servo_human_id=1, servo_human_id_range=(0, 1), servo_timeout=0, nema_timeout=0, sensorless=False):
        """ class init
        """
        self.motor = NemaMotor(
            dir_pin,
            step_pin,
            en_pin,
            nema_timeout=nema_timeout
        )
        self.motor.motor_enable(True)

        self.sensorless = sensorless
        self.current_id = -1
        if not self.sensorless:
            self.encoder = AS5048B(address=sensor_addr)
        self.sensor_zeroreg = sensor_zeroreg
        self._lock = threading.Lock()

        self.servo_monkey = Servo(
            servo_monkey_id,
            servo_monkey_id_range,
            servo_timeout,
        )
        self.servo_human = Servo(
            servo_human_id,
            servo_human_id_range,
            servo_timeout,
        )

    def motors_off(self):
        self.motor.motor_enable(False)
        for i in range(0, self.servo_human.servokit._channels):
            self.servo_human.servokit.servo[i].fraction = None

    def cleanup(self):
        self.motor.cleanup()
        if not self.sensorless:
            self.encoder.cleanup()
        self.servo_human.cleanup()
        self.servo_monkey.cleanup()

    def deploy(self, id, monkey=True, blocking=True, callback=None):
        self._lock.acquire()
        self._thread = threading.Thread(target=self._deploy, kwargs={
            "id": id, "monkey": monkey, "callback": callback})
        self._thread.start()
        if blocking:
            self.move_to_wait()

    def _deploy(self, id, monkey, callback=None):
        servo = self.servo_human
        if monkey:
            servo = self.servo_monkey
        self._move_to(id, monkey)
        servo.door_open = True
        time.sleep(1)
        servo.door_open = False
        time.sleep(1)
        self._lock.release()
        if callback is not None:
            callback()

    def move_to(self, id, monkey=True, blocking=True, callback=None):
        self._lock.acquire()
        self._thread = threading.Thread(target=self._move_to_helper, kwargs={
            "id": id, "monkey": monkey, "callback": callback})
        self._thread.start()
        if blocking:
            self.move_to_wait()

    def _move_to_helper(self, id, monkey, callback=None):
        self._move_to(id, monkey)
        self._lock.release()
        if callback is not None:
            callback()

    def _move_to(self, id, monkey):
        if self.sensorless and self.current_id == -1:
            self.current_id = id + self.COMPARTMENTS/2

        if monkey:
            id = id + self.COMPARTMENTS/2

        self.motor.motor_go(steps=self.getOffsetForID(id), clockwise=False)
        self.current_id = id
        time.sleep(.1)
        self.motor.motor_go(steps=self.getOffsetForID(id), clockwise=False)

    def move_to_wait(self, timeout=-1, spinlock=False):
        logging.debug("move to wait")

        if spinlock:
            # Spinlock
            timeout = time.time() + timeout   # timeout seconds from now
            while self._lock.locked():
                if time.time() > timeout:
                    logging.debug("timeout")
                    return False
                time.sleep(0.01)
            logging.debug("state reached")
            return True
        else:
            if self._lock.locked():
                self._thread.join(timeout)

    def getOffsetForID(self, id):

        if self.sensorless:
            sourceA = self.current_id * self.ANGLE_COMPARTMENT
        else:
            sourceA = self.encoder.angleR(unit=self.encoder.units.DEG)
        targetA = id * self.ANGLE_COMPARTMENT
        logging.debug("id: %d" % (id+1))
        logging.debug("current_id: %d" % (self.current_id+1))
        logging.debug("sourceA: %d" % (sourceA))
        logging.debug("targetA: %d" % (targetA))
        a = (targetA-sourceA+540) % 360-180
        logging.debug("a: %d" % (a))
        return -int(round(a/self.ANGLE_RES_STEPS, 0))
