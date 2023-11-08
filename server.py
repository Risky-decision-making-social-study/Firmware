import logging
import optparse
import socketserver
import sys

#from RPi import GPIO

from apparatus import queuelogger, util
from apparatus.apparatus import Apparatus
from apparatus.apparatus_config import config
from apparatus.server import Handler


def arg_dictionary(option, opt_str, value, parser):
    key, fname = "dictionary", value
    if '=' in value:
        mcu_name, fname = value.split('=', 1)
        key = "dictionary_" + mcu_name
    if parser.values.dictionary is None:
        parser.values.dictionary = {}
    parser.values.dictionary[key] = fname


def main():
    usage = "%prog [options] <config file>"
    opts = optparse.OptionParser(usage)
    opts.add_option("-l", "--logfile", dest="logfile",
                    help="write log to file instead of stderr")
    opts.add_option("-d", "--dictionary", dest="dictionary", type="string",
                    action="callback", callback=arg_dictionary,
                    help="file to read for mcu protocol dictionary")
    opts.add_option("-v", action="store_true", dest="verbose",
                    help="enable debug messages")
    options, args = opts.parse_args()
    if len(args) != 1:
        opts.error("Incorrect number of arguments")
    start_args = {'config_file': args[0]}

    debuglevel = logging.INFO
    if options.verbose:
        debuglevel = logging.DEBUG
    bglogger = None
    if options.logfile:
        start_args['log_file'] = options.logfile
        bglogger = queuelogger.setup_bg_logging(options.logfile, debuglevel)

    else:
        logging.basicConfig(format='[%(asctime)s.%(msecs)03d] [%(levelname)-6s] --- %(message)s (%(filename)s:%(lineno)s)',
                            datefmt='%Y-%m-%d:%H:%M:%S', level=debuglevel)

    logging.info("Starting Apparatus...")
    start_args['software_version'] = util.get_git_version()
    start_args['cpu_info'] = util.get_cpu_info()

    if bglogger is not None:
        versions = "\n".join([
            "Args: %s" % (sys.argv,),
            "Git version: %s" % (repr(start_args['software_version']),),
            "CPU: %s" % (start_args['cpu_info'],),
            "Python: %s" % (repr(sys.version),)])
        logging.info(versions)

    config.loadConfig(start_args["config_file"])
    import yaml
    logging.info("Config:\n%s" % yaml.dump(config.__dict__))

    GPIO.cleanup()

    GPIO.setmode(GPIO.BCM)

    config.apparatus_hw = Apparatus()
    config.apparatus_hw.init_hw()

    server = socketserver.TCPServer(
        ('', config.apparatus['port']), Handler,)
    logging.info('The server is running...')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        logging.info('Server stopped')
        server.shutdown()

    if config.apparatus_hw is not None:
        config.apparatus_hw.cleanup()
    if bglogger is not None:
        bglogger.stop()


if __name__ == '__main__':
    main()
