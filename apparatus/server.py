import logging
import pickle
import socketserver

from apparatus.apparatus import Apparatus


class Handler(socketserver.StreamRequestHandler):
    # no delay
    disable_nagle_algorithm = True
    HEADERSIZE = 4
    apparatus: Apparatus = None

    def handle(self):
        self.client = f'{self.client_address}'
        logging.info(f'Connected: {self.client}')
        try:
            self.initialize()
            self.apparatus_handler.startThread()
            self.process_commands()
        except IOError as e:
            logging.info(e)
        except Exception as e:
            logging.exception(e)
        finally:
            self.myclose()

    def myclose(self):
        logging.info("client left")
        self.apparatus.motors_off()
        self.apparatus.init_hw()
        self.apparatus_handler.close()

        logging.info(f'Closed: {self.client}')

    def send_dict(self, dict):
        logging.info(dict)
        msg: bytes = pickle.dumps(dict)
        msg = len(msg).to_bytes(self.HEADERSIZE, "little", signed=False)+msg

        self.wfile.write(msg)

    def recv_dict(self, bytes):
        return self.rfile.read(bytes)

    def process_commands(self):
        while True:
            head: bytes = self.recv_dict(self.HEADERSIZE)
            len: int = int.from_bytes(head, 'little', signed=False)
            dict = {}
            type = "error"
            if head == b'':
                # Client closed connection
                break
            if len:
                data = self.recv_dict(len)
                dict = pickle.loads(data)
            else:
                continue
            if "type" in dict:
                type = dict["type"]
                try:
                    self.run_apparatus_command(dict)
                    self.send_dict({"type": type, "success": True})
                    continue
                except Exception as e:
                    logging.exception(e)
                    self.send_dict(
                        {"type": type, "success": False, "msg": str(e)})
                    continue
            self.send_dict({"type": type, "success": False,
                           "msg": "Type not in dict"})

    def run_apparatus_command(self, dict):
        func = ""
        if "func" in dict:
            method = getattr(self.apparatus_handler, dict["func"])
            logging.debug(method)
            if callable(method):
                args = dict["args"]
                logging.debug(args)
                method(**args)

    def initialize(self):
        logging.info(f'Welcome {self.client}')
        #from apparatus.apparatus_handler_dummy import ApparatusServerHandlerDummy
        from apparatus.apparatus_config import config
        from apparatus.apparatus_handler import ApparatusServerHandler
        self.apparatus = config.apparatus_hw
        self.apparatus_handler = ApparatusServerHandler(
            server=self, apparatus=self.apparatus)
