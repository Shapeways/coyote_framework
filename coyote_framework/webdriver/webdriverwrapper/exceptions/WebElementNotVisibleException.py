from coyote_framework.webdriver.webdriverwrapper.exceptions import WebElementWrapperException

__author__ = 'justin'


class WebElementNotVisibleException(WebElementWrapperException.WebElementWrapperException):

    def __init__(self, element_wrapper, msg='WebElement was not visible', execute_on_error=None):
        try:
            location = element_wrapper.element.location
            msg += '; Element was located at (x:' + str(location['x']) + ', y:' + str(location['x']) + ')'
        finally:
            WebElementWrapperException.WebElementWrapperException.__init__(self, element_wrapper, msg, execute_on_error)