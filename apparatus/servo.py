import threading
from adafruit_servokit import ServoKit


class Servo(object):

    servokit: ServoKit = None
    channel: int = 0
    _timer: threading.Timer = None
    _servo_timeout: float = 0

    def __init__(self, channel_id, range, servo_timeout=0):
        self.servokit = ServoKit(channels=16, address=0x43)
        self.channel = channel_id
        self.range = range
        self._servo_timeout = servo_timeout

    _range = None
    _open_state = False

    def cleanup(self):
        # turn of servos
        for i in range(0, 16):
            self.servokit.servo[i].fraction = None

    @property
    def range(self):
        """I'm the 'x' property."""
        return self._range

    @range.setter
    def range(self, value):
        self._range = value
        self.servokit.servo[self.channel].set_pulse_width_range(*value)

    @property
    def door_open(self):
        """I'm the 'x' property."""
        return self._open_state

    @door_open.setter
    def door_open(self, value):
        self._open_state = value
        self.servokit.servo[self.channel].angle = 180 if not value else 0
        self._startTimeout()

    @property
    def lever_open(self):
        """I'm the 'x' property."""
        return self._open_state

    @lever_open.setter
    def lever_open(self, value):
        self._open_state = value
        self.servokit.servo[self.channel].angle = 180 if not value else 0
        self._startTimeout()

    def _startTimeout(self):
        if self._servo_timeout <= 0:
            return
        if self._timer is not None:
            self._timer.cancel()
        # Disable Servo after "_servo_timeout" sec.
        self._timer = threading.Timer(
            interval=self._servo_timeout,
            function=setattr,
            args=(self.servokit.servo[self.channel], 'angle', None),
        )
        self._timer.start()
