from coyote_framework.mixins.filesystem import create_directory

__author__ = 'justin'

import sys
import logging
import datetime

import os
from coyote_framework.util.apps.templating.template import build_string_from_method_args

loggers = []

FORMAT = '%(levelname)s: %(asctime)s: %(message)s'
DATE_FORMAT = '%m/%d/%Y %I:%M:%S %p'

# logging levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARN
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

DEFAULT_LEVEL = INFO


class log_on_failure:

    def __init__(self, error_message=None):
        self.error_message = error_message

    def __call__(self, fn):
        def return_function(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as E:
                message = build_string_from_method_args(self.error_message, args, kwargs)
                if len(args) > 0 and hasattr(args[0], 'logger'):
                    args[0].logger.error(message)
                else:
                    get().error(message)
                raise

        return return_function


def get():
    global loggers

    if len(loggers) > 0:
        return loggers[0]

    else:
        todays_date = str(datetime.date.today())
        logs_dir = create_directory('/tmp/coyote_framework/logs/' + todays_date)
        logs_file = logs_dir + '/' + todays_date + '.log'
        logging.basicConfig(format=FORMAT, datefmt=DATE_FORMAT, filename=logs_file, filemode='w')

        # logging streamhandler for log files
        _file = logging.StreamHandler()
        _file.setFormatter(logging.Formatter(FORMAT))
        _file.setLevel(DEFAULT_LEVEL)

        # logging streamhandler for standardout
        output = logging.StreamHandler(sys.stdout)

        logger = logging.getLogger(todays_date)
        logger.addHandler(logging.FileHandler(logs_file))
        logger.addHandler(output)
        logger.addHandler(_file)

        loggers.append(logger)
        return logger


def log(message, level=INFO):

    print message

    if level == INFO:
        get().info(message)

    elif level == DEBUG:
        get().debug(message)

    elif level == WARN:
        get().warning(message)

    elif level == ERROR:
        get().error(message)

    elif level == CRITICAL:
        get().critical(message)