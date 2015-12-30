from coyote_framework.webdriver.webdriverwrapper.exceptions import WebDriverWrapperException

__author__ = 'justin'


class WebDriverAssertionException(WebDriverWrapperException.WebDriverWrapperException):

    def __init__(self, driver_wrapper, msg, execute_on_error=None):
        try:
            if not isinstance(msg, basestring):
                msg = ''
            msg = 'Failed Assertion: ' + msg
        finally:
            WebDriverWrapperException.WebDriverWrapperException.__init__(self, driver_wrapper, msg, execute_on_error)