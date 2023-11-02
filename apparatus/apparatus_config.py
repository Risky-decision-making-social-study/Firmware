import logging
from configparser import SafeConfigParser

section_names = 'carousel1', 'carousel2'


class ApparatusConfiguration(object):
    apparatus_hw = None

    def __init__(self, *file_names):
        pass

    def evalDict(self, data, namespace):
        if isinstance(data, dict):
            return {k: self.evalDict(v, namespace) for k, v in data.items()}
        else:
            try:
                data = eval(data, *namespace)
            except Exception as e:
                logging.exception(e)
                logging.info("Exception caused by config value: %s" % data)
            return data

    def loadConfig(self, *file_names):
        parser = SafeConfigParser()
        parser.optionxform = str  # make option names case sensitive
        found = parser.read(file_names)
        if not found:
            raise ValueError('No config file found!')

        namespace = ({"__builtins__": None}, {'range': range})

        self.__dict__.update(self.evalDict(parser._sections, namespace))


config = ApparatusConfiguration()
