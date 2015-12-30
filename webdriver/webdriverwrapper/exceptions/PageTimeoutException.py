from coyote_framework.webdriver.webdriverwrapper.exceptions import WebDriverWrapperException

__author__ = 'justin'


class PageTimeoutException(WebDriverWrapperException.WebDriverWrapperException):

    def __init__(self, driver_wrapper, target_url=None, msg=None, execute_on_error=None):
        try:
            if not isinstance(msg, str):
                msg = ''
            else:
                msg += '; '
            msg += 'Timeout waiting for page to load || Current URL: {} || Target URL: {}'.format(
                driver_wrapper.current_url(), target_url)
        finally:
            WebDriverWrapperException.WebDriverWrapperException.__init__(self, driver_wrapper, msg, execute_on_error)