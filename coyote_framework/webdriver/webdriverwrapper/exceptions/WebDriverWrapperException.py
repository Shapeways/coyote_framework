from coyote_framework.webdriver.webdriverwrapper.support import JavascriptExecutor

__author__ = 'justin'

from selenium.common.exceptions import WebDriverException

from coyote_framework.log import Logger


class WebDriverWrapperException(WebDriverException):

    def __init__(self, driver_wrapper, msg='WebDriverWrapper Exception', execute_on_error=None):

        js_executor = JavascriptExecutor.JavascriptExecutor(driver_wrapper)
        error_message = None

        try:
            # error_message sometimes has encoding problems
            error_message = "Message: {} || Page Title: {} || Current URL: {}"\
                .format(msg, driver_wrapper.driver.title, driver_wrapper.driver.current_url)

            # insert the error message into the page
            js_executor.execute_template('messageInjectorTemplate', {'message': error_message})

        except Exception, e:
            error_message = 'Unable to build error message: {}'.format(e) if error_message is None else error_message

        finally:
            Logger.get().warn(error_message)
            WebDriverException.__init__(self, error_message)

        # pass it an anonymous function to execute on instantiation
        if execute_on_error is not None and hasattr(execute_on_error, '__call__'):
            execute_on_error()