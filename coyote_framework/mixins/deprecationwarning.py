from coyote_framework import log

__author__ = 'justin'

from coyote_framework.log.Logger import WARN


class deprecated:
    """Deprecation decorator to warn when a function is deprecated
        """
    # TODO provide deprecation method which supports static methods

    def __init__(self, warning=None):
        self.warning = warning

    def __call__(self, fn):
        def deprecated_function(*args, **kwargs):
            message = 'Function "{function_name}" is deprecated{warning_message}'.format(
                function_name=fn.__name__,
                warning_message=': {}'.format(self.warning) if self.warning is not None else '')

            try:
                log(message, WARN)
            except:
                print message

            return fn(*args, **kwargs)

        return deprecated_function

