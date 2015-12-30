from coyote_framework.webdriver.webdriverwrapper.exceptions import WebElementWrapperException

__author__ = 'justin'


class WebElementDoesNotExist(WebElementWrapperException.WebElementWrapperException):

    def __init__(self, element_wrapper, msg='WebElement does not exist', execute_on_error=None):

        WebElementWrapperException.WebElementWrapperException.__init__(self, element_wrapper, msg, execute_on_error)