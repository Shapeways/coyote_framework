"""
WebDriverJavascriptException module
"""
__author__ = 'justin'

from selenium.common.exceptions import WebDriverException

class WebDriverJavascriptException(WebDriverException):
    """
    Exception for javascript executions
    """
    def __init__(self, driver_wrapper, msg):
        try:
            if not isinstance(msg, str): msg = 'No message'
            msg = 'Error executing Javascript: ' + msg
        finally:
            WebDriverException.__init__(self, msg)