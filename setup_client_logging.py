import datetime
import logging

TIME_FORMAT_FILE = '%Y-%m-%d_%H-%M-%S'
LOG_FORMAT_STRING = '[%(asctime)s.%(msecs)03d] [%(levelname)-6s] --- %(message)s (%(filename)s:%(lineno)s)'
LOG_FORMAT_STRING_FILE = '[%(asctime)s] [%(levelname)-6s] --- %(message)s (%(filename)s:%(lineno)s)'
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'


def setup(script_name, debuglevel):

    timestamp = datetime.datetime.now().strftime(TIME_FORMAT_FILE)
    filename = "%s_%s" % (
        timestamp, script_name,)
    logFormatter = logging.Formatter(LOG_FORMAT_STRING, datefmt=LOG_DATEFMT)

    ch = logging.StreamHandler()
    ch.setLevel(debuglevel)

    fh = logging.FileHandler(
        "{0}/{1}.log".format("logs_clients", "%s" % (filename,)))
    fh.setFormatter(logFormatter)
    fh.setLevel(logging.DEBUG)

    logging.basicConfig(format=LOG_FORMAT_STRING,
                        datefmt=LOG_DATEFMT,
                        level=logging.DEBUG,
                        handlers=[ch, fh]
                        )
