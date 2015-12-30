from coyote_framework.webdriver.webdriverwrapper.exceptions import WebDriverWrapperException

__author__ = 'justin'


class WebElementWrapperException(WebDriverWrapperException.WebDriverWrapperException):

    def __init__(self, element_wrapper, msg='WebDriverWrapper Exception', execute_on_error=None):

        try:
            element_wrapper.highlight()

        finally:
            WebDriverWrapperException.WebDriverWrapperException.__init__(self, element_wrapper, msg, execute_on_error)