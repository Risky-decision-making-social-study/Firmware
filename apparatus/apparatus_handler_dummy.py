
import logging
import pickle
import threading
import time

from apparatus.apparatus_interface import ApparatusInterface
from apparatus.server import Handler


class ApparatusServerHandlerDummy(ApparatusInterface):
    _HEADERSIZE = 4
    server: Handler = None
    thread: threading.Thread = None

    def __init__(self, server) -> None:
        self.server = server

    def startThread(self):
        self._stop_async_send_thread = False
        self.thread = threading.Thread(
            target=self._async_send, args=(lambda: self._stop_async_send_thread,))
        self.thread.start()

    def _send_dict(self, dict):
        data: bytes = pickle.dumps(dict)
        msg: bytes = len(data).to_bytes(
            self._HEADERSIZE, "little", signed=False)+data
        self._socket.send(msg)

    def _async_send(self, stop_thread):
        while True:
            time.sleep(5)
            if stop_thread():
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

    def close(self):
        self._stop_async_send_thread = True
        self.thread.join()
        self.server.finish()

    def _localtodict(self, l: dict) -> dict:
        l.pop('self', None)
        return l

    def init_hw(self):
        logging.debug(self._localtodict(locals()))
        pass

    def hw_self_test(self):
        logging.debug(self._localtodict(locals()))
        pass

    def play_sound(self, file=None, volume=90, timestamp=None):
        logging.debug(self._localtodict(locals()))
        pass

    def empty_human(self):
        logging.debug(self._localtodict(locals()))
        pass

    def move_to(self, carousel_id, compartment_id, monkey=False, blocking=False):
        logging.debug(self._localtodict(locals()))
        pass

    def move_to_wait(self, carousel_id):
        logging.debug(self._localtodict(locals()))
        pass

    def deploy(self, carousel_id, compartment_id, monkey=False, blocking=False):
        logging.debug(self._localtodict(locals()))
        pass

    def deploy_wait(self, carousel_id):
        logging.debug(self._localtodict(locals()))
        pass

    def set_test_light(self, state, color=None, timestamp=None):
        logging.debug(self._localtodict(locals()))
        pass

    def set_human_light(self, state, color=None):
        logging.debug(self._localtodict(locals()))
        pass

    def set_light(self, color, timestamp=None):
        logging.debug(self._localtodict(locals()))
        pass

    def wait_lever_state(self, pin_io, state, timeout=-1, spinlock=False) -> bool:
        logging.debug(self._localtodict(locals()))
        pass

    def set_lever_open(self, state, timestamp=None):
        logging.debug(self._localtodict(locals()))
        pass
