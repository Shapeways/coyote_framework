from coyote_framework import log

__author__ = 'justin'

import time


class time_this_function:
    """An inaccurate decorator meant to time fucntion calls that take >1s (not for ms accuracy!)
    """

    def __init__(self, logger=None, datadog_key=''):
        self.logger = logger
        self.key = datadog_key

    def __call__(self, fn):
        def timed(*args, **kwargs):
            ts = time.time()
            return_val = fn(*args, **kwargs)
            te = time.time()

            elapsed = round(te - ts, 4)
            message = 'Function "{}" elapsed time: {} seconds'.format(fn.__name__, elapsed)

            if self.logger is not None:
                print message
                self.logger.info(message)
            else:
                try:
                    print message
                    log(message)
                except:
                    print message

            return return_val

        return timed

