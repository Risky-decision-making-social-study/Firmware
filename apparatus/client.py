#!/usr/bin/env python3

import logging
import pickle
import socket
import threading

import apparatus.apparatus_interface


class ApparatusClient(apparatus.apparatus_interface.ApparatusInterface):
    _HEADERSIZE = 4
    _socket: socket.socket
    _recv_thread: threading.Thread
    _stop_recv_thread: bool

    _sig_carousel = []

    _sig_io_touch_high: threading.Event
    _sig_io_touch_low: threading.Event
    _sig_io_switch_high: threading.Event
    _sig_io_switch_low: threading.Event
    _sig_io_switch_up_high: threading.Event
    _sig_io_switch_up_low: threading.Event

    _logging_touch_callback = None
    _logging_switch_callback = None
    _logging_switch_up_callback = None

    def __init__(self, host, port, logging_touch_callback=None, logging_switch_callback=None, logging_switch_up_callback=None) -> None:
        self._logging_touch_callback = logging_touch_callback
        self._logging_switch_callback = logging_switch_callback
        self._logging_switch_up_callback = logging_switch_up_callback

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        # self._socket.setblocking(False)

        self._sig_carousel = [{"_sig_move_to_wait": threading.Event(), "_sig_deploy":  threading.Event()},
                              {"_sig_move_to_wait": threading.Event(), "_sig_deploy":  threading.Event()}]

        self._sig_io_touch_high: threading.Event = threading.Event()
        self._sig_io_touch_low: threading.Event = threading.Event()
        self._sig_io_switch_high: threading.Event = threading.Event()
        self._sig_io_switch_low: threading.Event = threading.Event()
        self._sig_io_switch_up_high: threading.Event = threading.Event()
        self._sig_io_switch_up_low: threading.Event = threading.Event()

        self._stop_recv_thread = False
        self._recv_thread = threading.Thread(
            target=self._async_recv, args=(lambda: self._stop_recv_thread,))
        self._recv_thread.start()

        interface_methods = method_list = [
            func for func in dir(apparatus.apparatus_interface.ApparatusInterface) if not func.startswith('_') and callable(getattr(apparatus.apparatus_interface.ApparatusInterface, func))]

    def _send_dict(self, dict):
        data: bytes = pickle.dumps(dict)
        msg: bytes = len(data).to_bytes(
            self._HEADERSIZE, "little", signed=False)+data
        self._socket.send(msg)

    def _async_recv(self, stop_thread):
        while True:
            import select
            ready = select.select([self._socket], [], [], 10)
            if stop_thread():
                break
            if not ready[0]:
                continue

            head: bytes = self._socket.recv(self._HEADERSIZE)
            if head == '':
                break  # closed connection
            len: int = int.from_bytes(head, 'little', signed=False)
            if len:
                data = self._socket.recv(len)
                dict = pickle.loads(data)

            if "type" not in dict:
                # package not to spec
                continue

            logging.debug(dict["type"])

            # TODO implement recv

            if dict["type"] == "event":
                logging.debug(dict["event"])
            elif dict["type"] == "msg":
                logging.debug(dict["msg"])
            elif dict["type"] == "command":
                logging.debug(dict)
            elif dict["type"] == "wait_event":
                logging.debug(dict)
                if dict["func_name"] == 'move_to':
                    self._sig_carousel[dict["carousel_id"]
                                       ]["_sig_move_to_wait"].set()
                elif dict["func_name"] == 'deploy':
                    self._sig_carousel[dict["carousel_id"].set()
                                       ]["_sig_deploy_wait"]
            elif dict["type"] == "io_event":
                logging.debug(dict)
                if dict["name"] == 'LEVER_TOUCHS_IO':
                    if dict["state"]:
                        logging.debug("LEVER_TOUCHS_IO True")
                        self._sig_io_touch_high.set()
                        self._sig_io_touch_low.clear()  # arm since state change
                    else:
                        logging.debug("LEVER_TOUCHS_IO False")
                        self._sig_io_touch_low.set()
                        self._sig_io_touch_high.clear()  # arm since state change
                    # Callback for csv writer
                    if self._logging_touch_callback is not None:
                        timestamp = dict["timestamp"] if dict["timestamp"] is not None else None
                        self._logging_touch_callback(
                            dict["name"], dict["state"] == 1, timestamp)

                elif dict["name"] == 'LEVER_SWITCH_IO':
                    if dict["state"]:
                        logging.debug("LEVER_SWITCH_IO True")
                        self._sig_io_switch_high.set()
                        self._sig_io_switch_low.clear()  # arm since state change
                    else:
                        logging.debug("LEVER_SWITCH_IO False")
                        self._sig_io_switch_low.set()
                        self._sig_io_switch_high.clear()  # arm since state change
                    # Callback for csv writer
                    if self._logging_switch_callback is not None:
                        timestamp = dict["timestamp"] if dict["timestamp"] is not None else None

                        self._logging_switch_callback(
                            dict["name"], dict["state"] == 0, timestamp)

                elif dict["name"] == 'LEVER_SWITCH_UP_IO':
                    if dict["state"]:
                        logging.debug("LEVER_SWITCH_UP_IO True")
                        self._sig_io_switch_up_high.set()
                        self._sig_io_switch_up_low.clear()  # arm since state change
                    else:
                        logging.debug("LEVER_SWITCH_UP_IO False")
                        self._sig_io_switch_up_low.set()
                        self._sig_io_switch_up_high.clear()  # arm since state change
                    # Callback for csv writer
                    if self._logging_switch_up_callback is not None:
                        timestamp = dict["timestamp"] if dict["timestamp"] is not None else None

                        self._logging_switch_up_callback(
                            dict["name"], dict["state"] == 0, timestamp)

            # self.send_dict(data)

    def close_connection(self):
        self._stop_recv_thread = True
        self._recv_thread.join()
        try:
            self._socket.shutdown(socket.SHUT_WR)
        except Exception as e:
            logging.exception(e)
        self._socket.close()

    def _localtodict(self, l: dict) -> dict:
        l.pop('self', None)
        return l

    def init_hw(self):
        args = self._localtodict(locals())
        type = "command"
        func = self.init_hw.__name__
        self._send_dict({"type": type, "func": func, "args": args})
        # Wait for done signal (blocking)
        pass

    def hw_self_test(self):
        args = self._localtodict(locals())
        type = "command"
        func = self.hw_self_test.__name__
        self._send_dict({"type": type, "func": func, "args": args})
        # Wait for done signal (blocking)
        pass

    def play_sound(self, file=None, volume=90, timestamp=None):
        args = self._localtodict(locals())
        type = "command"
        func = self.play_sound.__name__
        self._send_dict({"type": type, "func": func,
                        "args": args})
        pass

    def empty_human(self):
        args = self._localtodict(locals())
        type = "command"
        func = self.empty_human.__name__
        self._send_dict({"type": type, "func": func, "args": args})
        # Wait for done signal (blocking)
        pass

    def move_to(self, carousel_id, compartment_id, monkey=False, blocking=False):
        args = self._localtodict(locals())
        type = "command"
        func = self.move_to.__name__
        # Arm Event
        self._sig_carousel[carousel_id]["_sig_move_to_wait"].clear()
        self._send_dict({"type": type, "func": func, "args": args})
        if blocking:
            self.move_to_wait(carousel_id)
        pass

    def move_to_wait(self, carousel_id, timeout=-1):
        self._sig_carousel[carousel_id]["_sig_move_to_wait"].wait(timeout)
        # Wait for move_to "done" signal to come back

    def deploy(self, carousel_id, compartment_id, monkey=False, blocking=False):
        args = self._localtodict(locals())
        type = "command"
        func = self.deploy.__name__
        self._send_dict({"type": type, "func": func, "args": args})
        if blocking:
            self.deploy_wait(carousel_id)
        pass

    def deploy_wait(self, carousel_id, timeout=-1):
        self._sig_carousel[carousel_id]["_sig_deploy"].wait(timeout)

    def set_test_light(self, state, color=None, timestamp=None):
        args = self._localtodict(locals())
        type = "command"
        func = self.set_test_light.__name__
        self._send_dict({"type": type, "func": func, "args": args})

    def set_human_light(self, state, color=None):
        args = self._localtodict(locals())
        type = "command"
        func = self.set_human_light.__name__
        self._send_dict({"type": type, "func": func, "args": args})

    def set_light(self, color, timestamp=None):
        args = self._localtodict(locals())
        type = "command"
        func = self.set_light.__name__
        self._send_dict({"type": type, "func": func, "args": args})

    def get_wait_lever_state_event(self, pin_io, state) -> threading.Event:
        if pin_io == self.LEVER_TOUCH:
            if state:
                return self._sig_io_touch_high
            else:
                return self._sig_io_touch_low
        if pin_io == self.LEVER_PULLED:
            if state:
                return self._sig_io_switch_high
            else:
                return self._sig_io_switch_low
        if pin_io == self.LEVER_RELEASED:
            if state:
                return self._sig_io_switch_up_high
            else:
                return self._sig_io_switch_up_low
            # Wait for state "done" signal to come back
        return None  # False->Timeout

    def wait_lever_state(self, pin_io, state, timeout=None, spinlock=False) -> bool:
        if pin_io == self.LEVER_TOUCH:
            if state:
                return self._sig_io_touch_high.wait(timeout)
            else:
                return self._sig_io_touch_low.wait(timeout)
        if pin_io == self.LEVER_PULLED:
            if state:
                return self._sig_io_switch_high.wait(timeout)
            else:
                return self._sig_io_switch_low.wait(timeout)
        if pin_io == self.LEVER_RELEASED:
            if state:
                return self._sig_io_switch_up_high.wait(timeout)
            else:
                return self._sig_io_switch_up_low.wait(timeout)
            # Wait for state "done" signal to come back
        return False  # False->Timeout

    def set_lever_open(self, state, timestamp=None):
        args = self._localtodict(locals())
        type = "command"
        func = self.set_lever_open.__name__
        self._send_dict({"type": type, "func": func, "args": args})
