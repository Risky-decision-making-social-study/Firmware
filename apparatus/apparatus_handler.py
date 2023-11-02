import logging
import pickle
import threading
import time
from datetime import datetime, timedelta

from apparatus.apparatus import Apparatus
from apparatus.apparatus_config import config
from apparatus.apparatus_interface import ApparatusInterface
from apparatus.server import Handler


class ApparatusServerHandler(ApparatusInterface):
    _HEADERSIZE = 4
    server: Handler = None
    thread: threading.Thread = None
    apparatus: Apparatus = None
    closed = False

    def __init__(self, server, apparatus) -> None:
        self.server = server
        self.apparatus = apparatus
        self.apparatus.set_io_callback(self.io_callback)
        self.apparatus.set_wait_callback(self.wait_callback)

    def startThread(self):
        self._stop_async_send_thread = False
        self.thread = threading.Thread(
            target=self._async_send, args=(lambda: self._stop_async_send_thread,))
        self.thread.start()

    def _send_dict(self, dict):
        if self.closed:
            return
        data: bytes = pickle.dumps(dict)
        msg: bytes = len(data).to_bytes(
            self._HEADERSIZE, "little", signed=False)+data
        self._socket.send(msg)

    def _async_send(self, stop_thread):
        while True:
            time.sleep(1)
            if stop_thread():
                break
            self.io_init()
            break
            if self.server.wfile.writable():
                try:
                    self.server.send_dict(
                        {"type": "msg", "msg": "heartbeat"})
                except IOError as e:
                    logging.info(e)
                except Exception as e:
                    logging.exception(e)
                finally:
                    # continue
                    pass

    io_last_state = {}

    def io_init(self):
        self.io_callback(config.lever['switch_io'],
                         'LEVER_SWITCH_IO',
                         self.apparatus.lever.get_switch_io_state(), forced=True)
        self.io_callback(config.lever['touch_io'],
                         'LEVER_TOUCHS_IO',
                         self.apparatus.lever.get_touch_io_state(), forced=True)
        self.io_callback(config.lever['switch_up_io'],
                         'LEVER_SWITCH_UP_IO',
                         self.apparatus.lever.get_switch_up_io_state(), forced=True)

    def io_callback(self, pin_io, name, state, forced=False):
        if "%s_%d" % (name, pin_io) not in self.io_last_state:
            self.io_last_state["%s_%d" % (name, pin_io)] = state
            old_state = not state
        else:
            old_state = self.io_last_state["%s_%d" % (name, pin_io)]

        timestamp = datetime.now()
        if pin_io == config.lever['touch_io']:
            timestamp -= timedelta(
                milliseconds=config.lever['touch_io_bounce_time'])
        if pin_io == config.lever['switch_io']:
            timestamp -= timedelta(
                milliseconds=config.lever['switch_io_bounce_time'])
        if pin_io == config.lever['switch_up_io']:
            timestamp -= timedelta(
                milliseconds=config.lever['switch_up_io_bounce_time'])

        if forced or state != old_state:
            self.io_last_state["%s_%d" % (name, pin_io)] = state
            self.server.send_dict(
                {"type": "io_event", "pin_io": pin_io, "name": name, "state": state, "timestamp": timestamp})

    def wait_callback(self, carousel_id, func_name):
        self.server.send_dict(
            {"type": "wait_event", "carousel_id": carousel_id, "func_name": func_name})

    def close(self):
        self._stop_async_send_thread = True
        self.closed = True
        self.thread.join()
        self.server.finish()

    def init_hw(self):
        self.apparatus.init_hw()
        pass

    def hw_self_test(self):
        self.apparatus.hw_self_test()

    def play_sound(self, file="on-status.mp3", volume=90, timestamp=None):
        if timestamp is not None:
            delay = (timestamp - datetime.now()).total_seconds()
            threading.Timer(delay, self.apparatus.play_sound,
                            args=(file, volume,)).start()
            return
        self.apparatus.play_sound(file, volume)

    def empty_human(self):
        self.apparatus.empty_human()

    def move_to(self, carousel_id, compartment_id, monkey=False, blocking=False):
        self.apparatus.move_to(carousel_id, compartment_id, monkey, blocking)

    def move_to_wait(self, carousel_id):
        self.apparatus.move_to_wait(carousel_id)

    def deploy(self, carousel_id, compartment_id, monkey=False, blocking=False):
        self.apparatus.deploy(carousel_id, compartment_id,
                              monkey, blocking)

    def deploy_wait(self, carousel_id):
        self.apparatus.deploy_wait(carousel_id)

    def set_test_light(self, state, color=None, timestamp=None):
        if timestamp is not None:
            delay = (timestamp - datetime.now()).total_seconds()
            threading.Timer(delay, self.apparatus.set_test_light,
                            args=(state, color,)).start()
            return
        self.apparatus.set_test_light(state, color)

    def set_human_light(self, state, color=None):
        self.apparatus.set_human_light(state, color)

    def set_light(self, color, timestamp=None):
        if timestamp is not None:
            delay = (timestamp - datetime.now()).total_seconds()
            threading.Timer(delay, self.apparatus.set_light,
                            args=(color,)).start()
            return
        self.apparatus.set_light(color)

    def wait_lever_state(self, pin_io, state, timeout=-1, spinlock=False) -> bool:
        # TODO Implement async Lever state wait with recv messages
        # self.apparatus.wait_lever_state(*args)
        pass

    def set_lever_open(self, state, timestamp=None):
        if timestamp is not None:
            delay = (timestamp - datetime.now()).total_seconds()
            threading.Timer(delay, self.apparatus.set_lever_open,
                            args=(state,)).start()
            return
        self.apparatus.set_lever_open(state)
