from coyote_framework.webdriver.webdriverwrapper.exceptions import WebDriverWrapperException

__author__ = 'justin'


class WebDriverTimeoutException(WebDriverWrapperException.WebDriverWrapperException):

    def __init__(self, driver_wrapper, timeout, locator, msg, execute_on_error=None):
        try:
            if not isinstance(msg, str):
                msg = ''

            if locator:
                msg += '; No element located by {0} after {1} seconds'.format(locator, timeout)
            elif timeout:
                msg += '; Timeout after {0} seconds'.format(timeout)
            else:
                msg = msg or 'WebDriver Timeout Exception, no message'
        finally:
            WebDriverWrapperException.WebDriverWrapperException.__init__(self, driver_wrapper, msg, execute_on_error)