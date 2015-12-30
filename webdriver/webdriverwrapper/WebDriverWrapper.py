'''
WebdriverWrapper Module

This module wraps Selenium Webdriver, and provides a cleaner, more consistent interface.  It also provides error
handling, and creates a more deterministic tool for web automation
'''
import httplib
import logging
import signal
import os
from urlparse import urlparse, urljoin

from selenium.common.exceptions import TimeoutException, NoAlertPresentException, UnexpectedAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from coyote_framework.webdriver.webdriverwrapper import WebElementWrapper
from coyote_framework.webdriver.webdriverwrapper.exceptions import WebDriverWrapperException, WebDriverTimeoutException, \
    PageTimeoutException
from coyote_framework.webdriver.webdriverwrapper.support import LocatorHandler as LH
from coyote_framework.webdriver.webdriverwrapper.support.locator import Locator
from coyote_framework.webdriver.webdriverwrapper.support import WebDriverWrapperAssertion as Assertion
from coyote_framework.webdriver.webdriverwrapper.support import JavascriptExecutor as JE
from support import staticreader


BROWSER_LOG_LEVEL_INFO = u'INFO'
BROWSER_LOG_LEVEL_DEBUG = u'DEBUG'
BROWSER_LOG_LEVEL_WARNING = u'WARNING'
BROWSER_LOG_LEVEL_SEVERE = u'SEVERE'


class quitting(object):
    """Context for webdriver to quit on exit

    Usage:
    >>> with quitting(webdriver.Firefox()) as driver:
    >>>     driver.get('http://google.com')
    """
    def __init__(self, driver):
        self.driver = driver

    def __enter__(self):
        """@rtype: WebDriverWrapper"""
        return self.driver

    def __exit__(self, *args, **kwargs):
        self.driver.quit()


class WebDriverWrapper(object):
    """
    WebdriverWrapper Module

    This module wraps Selenium Webdriver, and provides a cleaner, more consistent interface.  It also provides error
    handling, and creates a more deterministic tool for web automation
    """
    class Data(object):
        """Generic holder for data tied to the driver"""
        pass

    def __init__(self, driver, options=None, display=None, *args, **kwargs):
        """
        @type driver: RemoteWebDriver
        """
        logger = logging.getLogger(__name__)

        if options is None:
            options = {}

        options.update(kwargs)

        self.driver = driver
        try:
            self.driver_pid = driver.binary.process.pid
        except AttributeError:
            self.driver_pid = None

        logger.debug('WebDriver server url is: {}'.format(self.get_server_url()))
        logger.debug('WebDriver browser pid is: {}'.format(self.driver_pid))

        self.display = display
        self.display_pid = display.pid if display else None
        logger.debug('WebDriver display pid is: {}'.format(self.driver_pid))

        self.implicit_wait = options['implicit_wait'] if 'implicit_wait' in options else 1
        self.timeout = options['timeout'] if 'timeout' in options else 45
        self.user_wait_timeout = options['user_wait_timeout'] if 'user_wait_timeout' in options else 180
        self.find_attempts = options['find_attempts'] if 'find_attempts' in options else 2
        self.maximize_window = options['maximize_window'] if 'maximize_window' in options else False
        self.page_load_timeout = options['page_load_timeout'] if 'page_load_timeout' in options else self.timeout
        self.ignore_page_load_timeouts = options['ignore_page_load_timeouts'] if 'ignore_page_load_timeouts' in options else False
        self.browser_logs = []
        self.locator_handler = LH.LocatorHandler
        self.js_executor = JE.JavascriptExecutor(self)
        self.assertion = Assertion.WebDriverWrapperAssertion(self, self.timeout, self.implicit_wait)

        self.action_callbacks = options.get('action_callbacks') or []  # Functions to call at the end of each action
        self.paused = False

        # configure driver based on settings
        self.driver.implicitly_wait(self.implicit_wait)
        self.driver.set_page_load_timeout(self.page_load_timeout)
        if self.maximize_window is True:
            self.driver.maximize_window()

    def __str__(self):
        message = "<WebDriverWrapper: "

        try:
            message += "timeout: " + str(self.timeout) + ", "
            message += "implicit_wait: " + str(self.implicit_wait) + ", "
            message += "find_attempts: " + str(self.find_attempts) + " "
        except Exception:
            message += ' -- (properties omitted)'
        finally:
            message += ">"

        return message

    def __repr__(self):
        """
        Return self as string for repr
        """
        return self.__str__()

    def wrap_driver(self, driver):
        """
        @type driver webdriver
        """
        self.driver = driver

    def get_server_url(self):
        """Returns the url of the standalone server used for remote web connections urls

        @return: Selenium server url
        """
        return self.driver.command_executor._url

    def get_port(self):
        """Gets the port of the command executor

        @rtype: int
        @return: Port
        """
        return self.driver.command_executor.profile.port

    def get_profile_dir(self):
        """The path of the command executor's profile dir

        @return: Temp directory
        """
        return self.driver.command_executor.profile.path

    def get_profile_file(self):
        """The path of the command executor's profile

        @return: File path
        """
        return self.driver.command_executor.profile.userPrefs

    #
    # WebDriver Properties
    #

    def current_url(self):
        """
        @return current URL
        """
        return self.execute_and_handle_webdriver_exceptions(lambda *args, **kwargs: self.driver.current_url)

    def name(self):
        """
        @return name of driver
        """
        return self.execute_and_handle_webdriver_exceptions(lambda *args, **kwargs: self.driver.name)

    def page_source(self):
        """
        @return Source of the current page
        """
        return self.execute_and_handle_webdriver_exceptions(lambda *args, **kwargs: self.driver.page_source)

    def title(self):
        """
        @return <title> content of the current page
        """
        return self.execute_and_handle_webdriver_exceptions(lambda *args, **kwargs: self.driver.title)

    #
    # WebDriver Navigation
    #

    def get(self, url):
        """
        Alias for 'visit' method; use 'visit' please

        url -- An absolute or relative url stored as a string
        """
        return self.visit(url)

    def visit(self, url=''):
        """
        Driver gets the provided url in the browser, returns True if successful

        url -- An absolute or relative url stored as a string
        """
        def _visit(url):
            if len(url) > 0 and url[0] == '/':
                # url's first character is a forward slash; treat as relative path
                path = url
                full_url = self.driver.current_url
                parsed_url = urlparse(full_url)
                base_url = str(parsed_url.scheme) + '://' + str(parsed_url.netloc)
                url = urljoin(base_url, path)

            try:
                return self.driver.get(url)
            except TimeoutException:
                if self.ignore_page_load_timeouts:
                    pass
                else:
                    raise PageTimeoutException.PageTimeoutException(self, url)

        return self.execute_and_handle_webdriver_exceptions(lambda: _visit(url))

    def back(self):
        """
        Navigate to the previous page
        """
        return self.driver.back()

    def close(self):
        """
        Close the driver
        """
        return self.driver.close()

    def forward(self):
        """
        Navigate forward
        """
        return self.driver.forward()

    def refresh(self):
        """
        Refresh the current page
        """
        return self.driver.refresh()

    def switch_to_iframe(self, iframe):
        """
        @type iframe:   webdriverwrapper.WebElementWrapper
        @param iframe:  iframe to select
        @return:        driver w/ selected iframe
        """
        return self.driver.switch_to_frame(iframe.element)

    def is_alert_present(self):
        """Tests if an alert is present

        @return: True if alert is present, False otherwise
        """
        current_frame = None
        try:
            current_frame = self.driver.current_window_handle
            a = self.driver.switch_to_alert()
            a.text
        except NoAlertPresentException:
            # No alert
            return False
        except UnexpectedAlertPresentException:
            # Alert exists
            return True
        finally:
            if current_frame:
                self.driver.switch_to_window(current_frame)
        return True

    def switch_to_alert(self):
        """
        @return: javascript alert object
        """
        # TODO: for the switch_to_xxxx methods, add a wait_for_xxxx and call that
        # (alerts/windows may not be present for a split second)
        return self.driver.switch_to_alert()

    def switch_to_window(self, window_name):
        """
        @param window_name: name of the window
        @return:            the new window handle
        """
        return self.driver.switch_to_window(window_name)

    def switch_to_default_content(self):
        """

        @return: driver w/ default content
        """
        return self.driver.switch_to_default_content()

    def current_window_handle(self):
        """
        @return: Current window handle
        """
        return self.driver.current_window_handle

    def window_handles(self):
        """
        @return:    all open window handles
        """
        return self.driver.window_handles


    #
    # WebDriver Finds
    #

    def find(self, locator, find_all=False, search_object=None, force_find=False, exclude_invisible=False):
        """
        Attempts to locate an element, trying the number of times specified by the driver wrapper;
        Will throw a WebDriverWrapperException if no element is found

        @type locator:          webdriverwrapper.support.locator.Locator
        @param locator:         the locator or css string used to query the element
        @type find_all:         bool
        @param find_all:        set to True to locate all located elements as a list
        @type search_object:    webdriverwrapper.WebElementWrapper
        @param force_find:      If true will use javascript to find elements
        @type force_find:       bool
        @param search_object:   A WebDriver or WebElement object to call find_element(s)_by_xxxxx
        """
        search_object = self.driver if search_object is None else search_object
        attempts = 0

        while attempts < self.find_attempts + 1:
            if bool(force_find):
                js_locator = self.locator_handler.parse_locator(locator)

                if js_locator.By != 'css selector':
                    raise ValueError(
                        'You must use a css locator in order to force find an element; this was "{}"'.format(
                            js_locator))

                elements = self.js_executor.execute_template_and_return_result(
                    'getElementsTemplate.js', variables={'selector': js_locator.value})
            else:
                elements = self.locator_handler.find_by_locator(search_object, locator, True)

            # Save original elements found before applying filters to the list
            all_elements = elements

            # Check for only visible elements
            visible_elements = elements
            if exclude_invisible:
                visible_elements = [element for element in all_elements if element.is_displayed()]
                elements = visible_elements

            if len(elements) > 0:
                if find_all is True:
                    # return list of wrapped elements
                    for index in range(len(elements)):
                        elements[index] = WebElementWrapper.WebElementWrapper(self, locator, elements[index],
                                                                              search_object=search_object)

                    return elements

                elif find_all is False:
                    # return first element
                    return WebElementWrapper.WebElementWrapper(self, locator, elements[0], search_object=search_object)

            else:
                if attempts >= self.find_attempts:
                    if find_all is True:  # returns an empty list if finding all elements
                        return []
                    else:  # raise exception if attempting to find one element
                        error_message = "Unable to find element after {0} attempts with locator: {1}".format(
                            attempts,
                            locator
                        )

                        # Check if filters limited the results
                        if exclude_invisible and len(visible_elements) == 0 and len(all_elements) > 0:
                            error_message = "Elements found using locator {}, but none were visible".format(locator)

                        raise WebDriverWrapperException.WebDriverWrapperException(self, error_message)
                else:
                    attempts += 1

    def _find_immediately(self, locator, search_object=None):
        '''
        Attempts to immediately find elements on the page without waiting

        @type locator:          webdriverwrapper.support.locator.Locator
        @param locator:         Locator object describing
        @type search_object:    webdriverwrapper.WebElementWrapper
        @param search_object:   Optional WebElement to start search with.  If null, search will be on self.driver


        @return:                Single WebElemetnWrapper if find_all is False,
                                list of WebElementWrappers if find_all is True
        '''
        search_object = self.driver if search_object is None else search_object
        elements = self.locator_handler.find_by_locator(search_object, locator, True)
        return [WebElementWrapper.WebElementWrapper(self, locator, element) for element in elements]

    def find_all(self, locator, search_object=None, force_find=False):
        '''
        Find all elements matching locator

        @type locator:          webdriverwrapper.support.locator.Locator
        @param locator:         Locator object describing

        @rtype:                 list[WebElementWrapper]
        @return:                list of WebElementWrappers
        '''
        return self.find(locator=locator, find_all=True, search_object=search_object, force_find=force_find)

    def find_by_dynamic_locator(self, template_locator, variables, find_all=False, search_object=None):
        '''
        Find with dynamic locator

        @type template_locator:         webdriverwrapper.support.locator.Locator
        @param template_locator:        Template locator w/ formatting bits to insert
        @type variables:                dict
        @param variables:               Dictionary of variable substitutions
        @type find_all:                 bool
        @param find_all:                True to find all elements immediately, False for find single element only
        @type search_object:            webdriverwrapper.WebElementWrapper
        @param search_object:           Optional WebElement to start search with.
                                        If null, search will be on self.driver

        @rtype:                         webdriverwrapper.WebElementWrapper or list()
        @return:                        Single WebElemetnWrapper if find_all is False,
                                        list of WebElementWrappers if find_all is True
        '''
        template_variable_character = '%'
        # raise an exception if user passed non-dictionary variables
        if not isinstance(variables, dict):
            raise TypeError('You must use a dictionary to populate locator variables')

        # replace all variables that match the keys in 'variables' dict
        locator = ""
        for key in variables.keys():
            locator = template_locator.replace(template_variable_character + key, variables[key])

        return self.find(locator, find_all, search_object)

    def find_all_by_dynamic_locator(self, template_locator, variables):
        '''
        Find with dynamic locator

        @type template_locator:         webdriverwrapper.support.locator.Locator
        @param template_locator:        Template locator w/ formatting bits to insert
        @type variables:                dict
        @param variables:               Dictionary of variable substitutions

        @rtype:                         webdriverwrapper.WebElementWrapper or list()
        @return:                        Single WebElemetnWrapper if find_all is False,
                                        list of WebElementWrappers if find_all is True
        '''
        return self.find_by_dynamic_locator(template_locator, variables, True)

    def is_present(self, locator, search_object=None):
        """
        Determines whether an element is present on the page, retrying once if unable to locate

        @type locator:                  webdriverwrapper.support.locator.Locator
        @param locator:                 the locator or css string used to query the element
        @type search_object:            webdriverwrapper.WebElementWrapper
        @param search_object:           Optional WebElement to start search with.
                                        If null, search will be on self.driver
        """
        all_elements = self._find_immediately(locator, search_object=search_object)

        if all_elements is not None and len(all_elements) > 0:
            return True
        else:
            return False


    def is_present_no_wait(self, locator):
        """
        Determines whether an element is present on the page with no wait

        @type locator:  webdriverwrapper.support.locator.Locator
        @param locator: the locator or css string used to query the element
        """

        # first attempt to locate the element

        def execute():
            '''
            Generic function to execute wait
            '''
            return True if len(self.locator_handler.find_by_locator(self.driver, locator, True)) < 0 else False

        return self.execute_and_handle_webdriver_exceptions(
            execute, timeout=0, locator=locator, failure_message='Error running webdriver.find_all.')


    #
    # WebDriver Waits
    #

    def wait_until(self, wait_function, failure_message=None, timeout=None):
        """
        Base wait method: called by other wait functions to execute wait

        @type wait_function:    types.FunctionType
        @param wait_function:   Generic function to be executed
        @type failure_message:  str
        @param failure_message: Message to fail with if exception is raised
        @type timeout:          int
        @param timeout:         timeout override

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        timeout = timeout if timeout is not None else self.timeout
        failure_message = failure_message if failure_message is not None else \
            'Timeout waiting for custom function to return True'

        def wait():
            '''
            Wait function passed to executor
            '''
            return WebDriverWait(self, timeout).until(lambda dw: wait_function())

        return self.execute_and_handle_webdriver_exceptions(wait, timeout, None, failure_message)

    def wait_for(self, locator, timeout=None):
        """
        Waits until an element can be found (alias for wait_until_present)

        @type locator:  webdriverwrapper.support.locator.Locator
        @param locator: the locator or css string to search for the element
        @type timeout:  int
        @param timeout:  the maximum number of seconds the driver will wait before timing out

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found"""
        return self.wait_until_present(locator, timeout)

    def wait_until_present(self, locator, timeout=None, failure_message='Timeout waiting for element to be present'):
        """
        Waits for an element to be present

        @type locator:  webdriverwrapper.support.locator.Locator
        @param locator: the locator or css string to search for the element
        @type timeout:  int
        @param timeout:  the maximum number of seconds the driver will wait before timing out

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        timeout = timeout if timeout is not None else self.timeout

        def wait():
            '''
            Wait function passed to executor
            '''
            element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(
                (self.locator_handler.parse_locator(locator).By, self.locator_handler.parse_locator(locator).value)))
            return WebElementWrapper.WebElementWrapper(self, locator, element)

        return self.execute_and_handle_webdriver_exceptions(
            wait, timeout, locator, failure_message=failure_message)

    def wait_until_not_present(self, locator, timeout=None):
        """
        Waits for an element to no longer be present

        @type locator:  webdriverwrapper.support.locator.Locator
        @param locator: the locator or css string to search for the element
        @type timeout:  int
        @param timeout:  the maximum number of seconds the driver will wait before timing out

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        # TODO: rethink about neg case with is_present and waiting too long
        timeout = timeout if timeout is not None else self.timeout
        this = self  # for passing WebDriverWrapperReference to WebDriverWait

        def wait():
            '''
            Wait function pasted to executor
            '''
            return WebDriverWait(self.driver, timeout).until(lambda d: not this.is_present(locator))

        return self.execute_and_handle_webdriver_exceptions(
            wait, timeout, locator, 'Timeout waiting for element not to be present')

    def wait_until_visibility_of(self, locator, timeout=None,
                                 failure_message='Timeout waiting for element to be visible'):
        """
        Waits for an element to be visible

        @type locator:  webdriverwrapper.support.locator.Locator
        @param locator: the locator or css string to search for the element
        @type timeout:  int
        @param timeout:  the maximum number of seconds the driver will wait before timing out

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        timeout = timeout if timeout is not None else self.timeout

        def wait():
            '''
            Wait function passed to executor
            '''
            element = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(
                (self.locator_handler.parse_locator(locator).By, self.locator_handler.parse_locator(locator).value)))
            return WebElementWrapper.WebElementWrapper(self, locator, element)

        return self.execute_and_handle_webdriver_exceptions(
            wait,
            timeout,
            locator,
            failure_message
        )

    def wait_until_invisibility_of(self, locator, timeout=None):
        """
        Waits for an element to be invisible

        @type locator:  webdriverwrapper.support.locator.Locator
        @param locator: the locator or css string to search for the element
        @type timeout:  int
        @param timeout:  the maximum number of seconds the driver will wait before timing out

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        timeout = timeout if timeout is not None else self.timeout

        def wait():
            '''
            Wait function passed to executor
            '''
            element = WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(
                (self.locator_handler.parse_locator(locator).By, self.locator_handler.parse_locator(locator).value)))
            return WebElementWrapper.WebElementWrapper(self, locator, element)

        return self.execute_and_handle_webdriver_exceptions(
            wait, timeout, locator, 'Timeout waiting for element to be invisible')

    def wait_until_clickable(self, locator, timeout=None):
        """
        Waits for an element to be clickable

        @type locator:  webdriverwrapper.support.locator.Locator
        @param locator: the locator or css string to search for the element
        @type timeout:  int
        @param timeout:  the maximum number of seconds the driver will wait before timing out

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        timeout = timeout if timeout is not None else self.timeout

        def wait():
            '''
            Wait function passed to executor
            '''
            element = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(
                (self.locator_handler.parse_locator(locator).By, self.locator_handler.parse_locator(locator).value)))

            return WebElementWrapper.WebElementWrapper(self, locator, element)

        return self.execute_and_handle_webdriver_exceptions(
            wait, timeout, locator, 'Timeout waiting for element to be clickable')

    def wait_until_stale(self, locator, timeout=None):
        """
        Waits for an element to be stale in the DOM

        @type locator:  webdriverwrapper.support.locator.Locator
        @param locator: the locator or css string to search for the element
        @type timeout:  int
        @param timeout:  the maximum number of seconds the driver will wait before timing out

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        timeout = timeout if timeout is not None else self.timeout

        def wait():
            '''
            Wait function passed to executor
            '''
            element = WebDriverWait(self.driver, timeout).until(EC.staleness_of(
                (self.locator_handler.parse_locator(locator).By, self.locator_handler.parse_locator(locator).value)))

            return WebElementWrapper.WebElementWrapper(self, locator, element)

        return self.execute_and_handle_webdriver_exceptions(
            wait, timeout, locator, 'Timeout waiting for element to become stale')

    # TODO: more precise exception for non-element timeouts
    def wait_until_title_contains(self, partial_title, timeout=None):
        """
        Waits for title to contain <partial_title>

        @type partial_title:    str
        @param partial_title:   the partial title to locate
        @type timeout:          int
        @param timeout:         the maximum number of seconds the driver will wait before timing out

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        timeout = timeout if timeout is not None else self.timeout

        def wait():
            '''
            Wait function passed to executor
            '''
            return WebDriverWait(self.driver, timeout).until(EC.title_contains(partial_title))

        return self.execute_and_handle_webdriver_exceptions(
            wait, timeout, partial_title, 'Timeout waiting for title to contain: ' + str(partial_title))

    def wait_until_title_is(self, title, timeout=None):
        """
        Waits for title to be exactly <partial_title>

        @type title:    str
        @param title:   the exact title to locate
        @type timeout:          int
        @param timeout:         the maximum number of seconds the driver will wait before timing out

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        timeout = timeout if timeout is not None else self.timeout

        def wait():
            '''
            Wait function passed to executor
            '''
            return WebDriverWait(self.driver, timeout).until(EC.title_is(title))

        return self.execute_and_handle_webdriver_exceptions(
            wait, timeout, title, 'Timeout waiting for title to be: ' + str(title))
    def wait_until_alert_is_present(self, timeout=None):
        """
        Waits for an alert to be present

        @type timeout:          int
        @param timeout:         the maximum number of seconds the driver will wait before timing out

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        timeout = timeout if timeout is not None else self.timeout
        locator = None

        def wait():
            '''
            Wait function passed to executor
            '''
            return WebDriverWait(self.driver, timeout).until(EC.alert_is_present())

        return self.execute_and_handle_webdriver_exceptions(
            wait, timeout, locator, 'Timeout waiting for alert to be present')

    def wait_until_text_contains(self, locator, text, timeout=None):
        """
        Waits for an element's text to contain <text>

        @type locator:          webdriverwrapper.support.locator.Locator
        @param locator:         locator used to find element
        @type text:             str
        @param text:            the text to search for
        @type timeout:          int
        @param timeout:         the maximum number of seconds the driver will wait before timing out

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        timeout = timeout if timeout is not None else self.timeout
        this = self

        self.wait_for(locator) # first check that element exists

        def wait():
            '''
            Wait function passed to executor
            '''
            WebDriverWait(self.driver, timeout).until(lambda d: text in this.find(locator).text())
            return this.find(locator)

        return self.execute_and_handle_webdriver_exceptions(
            wait, timeout, locator, 'Timeout waiting for text to contain: ' + str(text))

    def wait_until_text_is(self, locator, text, timeout=None):
        """
        Waits for an element's text to exactly match <text>

        @type locator:          webdriverwrapper.support.locator.Locator
        @param locator:         locator used to find element
        @type text:             str
        @param text:            the text to search for
        @type timeout:          int
        @param timeout:         the maximum number of seconds the driver will wait before timing out

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        timeout = timeout if timeout is not None else self.timeout
        this = self

        self.wait_for(locator) # first check that element exists

        def wait():
            '''
            Wait function passed to executor
            '''
            WebDriverWait(self.driver, timeout).until(lambda d: text == this.find(locator).text())
            return this.find(locator)

        return self.execute_and_handle_webdriver_exceptions(
            wait, timeout, locator, 'Timeout waiting for text to be: ' + str(text))

    def wait_until_text_is_not_empty(self, locator, timeout=None):
        """
        Waits for an element's text to not be empty

        @type locator:          webdriverwrapper.support.locator.Locator
        @param locator:         locator used to find element
        @type timeout:          int
        @param timeout:         the maximum number of seconds the driver will wait before timing out

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        timeout = timeout if timeout is not None else self.timeout

        self.wait_for(locator) # first check that element exists

        def wait():
            '''
            Wait function passed to executor
            '''
            WebDriverWait(self.driver, timeout).until(lambda d: len(self.find(locator).text()) > 0)
            return self.find(locator)

        return self.execute_and_handle_webdriver_exceptions(
            wait, timeout, locator, 'Timeout waiting for element to contain some text')

    def wait_until_page_source_contains(self, text, timeout=None):
        """
        Waits for the page source to contain <text>

        @type text:             str
        @param text:            the text to search for
        @type timeout:          int
        @param timeout:         the maximum number of seconds the driver will wait before timing out

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        timeout = timeout if timeout is not None else self.timeout

        def wait():
            '''
            Wait function passed to executor
            '''
            WebDriverWait(self.driver, timeout).until(lambda d: text in self.page_source())
            return self.page_source()

        return self.execute_and_handle_webdriver_exceptions(
            wait, timeout, text, 'Timeout waiting for source to contain: {}'.format(text))

    def wait_until_jquery_requests_are_closed(self, timeout=None):
        """Waits for AJAX requests made through

        @type timeout:     int
        @param timeout:    the maximum number of seconds the driver will wait before timing out
        @return: None
        """
        timeout = timeout if timeout is not None else self.timeout

        def wait():
            '''
            Wait function passed to executor
            '''
            WebDriverWait(self.driver, timeout).until(
                lambda d: self.js_executor.execute_template('isJqueryAjaxComplete', {}))
            return True

        return self.execute_and_handle_webdriver_exceptions(
            wait, timeout, None, 'Timeout waiting for all jQuery AJAX requests to close')

    def execute_and_handle_webdriver_exceptions(self, function_to_execute, timeout=None, locator=None, failure_message=None):
        """
        Executor for wait functions

        @type function_to_execute:  types.FunctionType
        @param function_to_execute: wait function specifying the type of wait
        @type timeout:              int
        @param timeout:             the maximum number of seconds the driver will wait before timing out
        @type locator:              webdriverwrapper.support.locator.Locator
        @param locator:             locator used to find element
        @type failure_message:      str
        @param failure_message:     message shown in exception if wait fails

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        logger = logging.getLogger(__name__)
        try:
            val = function_to_execute()
            for cb in self.action_callbacks:
                cb.__call__(self)
            return val

        except TimeoutException:
            raise WebDriverTimeoutException.WebDriverTimeoutException(self, timeout, locator, failure_message)

        except httplib.BadStatusLine, e:
            logger.error('BadStatusLine error raised on WebDriver action (line: {}, args:{}, message: {})'.format(
                e.line,
                e.args,
                e.message
            ))
            raise
        
        except httplib.CannotSendRequest:
            logger.error('CannotSendRequest error raised on WebDriver action')
            raise

        except UnexpectedAlertPresentException:
            # NOTE: handling alerts in this way expects that WebDriver does not dismiss unexpected alerts. That
            # setting can be changed by modifying the unexpectedAlertBehaviour setting
            msg = '<failed to parse message from alert>'
            try:
                a = self.driver.switch_to_alert()
                msg = a.text
            except Exception, e:
                msg = '<error parsing alert due to {} (note: parsing ' \
                      'alert text expects "unexpectedAlertBehaviour" to be set to "ignore")>'.format(e)
                logger.critical(msg)
            finally:
                logger.error('Unexpected alert raised on a WebDriver action; alert message was: {}'.format(msg))
                raise UnexpectedAlertPresentException('Unexpected alert on page, alert message was: "{}"'.format(msg))

    #
    # Browser Interaction
    #

    def get_screenshot_as_png(self):
        """Gets the screenshot of the page as binary data

        @return: The binary data of the screenshot
        """
        return self.driver.get_screenshot_as_png()

    def execute_script(self, script, args=None):
        """
        JavaScript executor

        @type script:   str
        @param script:  javascript to execute
        @type args:     dict
        @param args:    dict of args

        @rtype:                 webdriverwrapper.WebElementWrapper
        @return:                Returns the element found
        """
        return self.js_executor.execute_script(script, args)

    def pause_and_wait_for_user(self, timeout=None, prompt_text='Click to resume (WebDriver is paused)'):
        """Injects a radio button into the page and waits for the user to click it; will raise an exception if the
        radio to resume is never checked

        @return: None
        """
        timeout = timeout if timeout is not None else self.user_wait_timeout
        # Set the browser state paused
        self.paused = True

        def check_user_ready(driver):
            """Polls for the user to be "ready" (meaning they checked the checkbox) and the driver to be unpaused.
            If the checkbox is not displayed (e.g. user navigates the page), it will re-insert it into the page

            @type driver: WebDriverWrapper
            @param driver: Driver to execute
            @return: True if user is ready, false if not
            """
            if driver.paused:
                if driver.is_user_ready():
                    # User indicated they are ready; free the browser lock
                    driver.paused = False
                    return True
                else:
                    if not driver.is_present(Locator('css', '#webdriver-resume-radio', 'radio to unpause webdriver')):
                        # Display the prompt
                        pause_html = staticreader.read_html_file('webdriverpaused.html')\
                            .replace('\n', '')\
                            .replace('PROMPT_TEXT', prompt_text)
                        webdriver_style = staticreader.read_css_file('webdriverstyle.css').replace('\n', '')


                        # Insert the webdriver style
                        driver.js_executor.execute_template_and_return_result(
                            'injectCssTemplate.js',
                            {'css': webdriver_style})

                        # Insert the paused html
                        driver.js_executor.execute_template_and_return_result(
                            'injectHtmlTemplate.js',
                            {'selector': 'body', 'html': pause_html})
            return False

        self.wait_until(
            lambda: check_user_ready(self),
            timeout=timeout,
            failure_message='Webdriver actions were paused but did not receive the command to continue. '
                            'You must click the on-screen message to resume.'
        )

        # Remove all injected elements
        self.js_executor.execute_template_and_return_result(
            'deleteElementsTemplate.js',
            {'selector': '.webdriver-injected'}
        )

    def is_process_running(self):
        """Checks if the driver process is running

        @return: True if PID present
        """
        try:
            os.kill(self.driver_pid, 0)
        except OSError:
            return False
        else:
            return True

    def is_user_ready(self):
        """Checks if the radio button indicating webdriver is paused is present and unchecked

        @rtype: bool
        @return: True if the paused radio is present on the page and unchecked; false otherwise
        """
        user_ready = not self.js_executor.execute_template_and_return_result('isWaitingForUser.js', {})
        return user_ready

    def add_cookie(self, cookie_dict):
        """Adds cookie with dictionary, requires keys "name" and "value" and takes optional keys: "path," "domain,"
        "secure", and "expiry"

        @type cookie_dict:  dict
        @param cookie_dict: dictionary of cookies. requires keys "name" and "value" and takes optional keys:
                             "path," "domain," "secure", and "expiry"

        """
        return self.driver.add_cookie(cookie_dict)

    def delete_all_cookies(self):
        """
        Delete all cookies from current session
        """
        return self.driver.delete_all_cookies()

    def delete_cookie(self, name):
        """
        Delete specific cookie from current session

        @type name:     str
        @params name:   name of cookie to delete
        """
        return self.driver.delete_cookie(name)

    def get_cookie(self, name):
        """
        Retrieve specific cookie from current session

        @type name:     str
        @params name:   name of cookie to retrieve
        """
        return self.driver.get_cookie(name)

    def get_cookies(self):
        """
        Retrieve all cookies
        """
        return self.driver.get_cookies()

    def get_browser_log(self, levels=None):
        """Gets the console log of the browser

        @type levels:
        @return: List of browser log entries
        """
        logs = self.driver.get_log('browser')
        self.browser_logs += logs
        if levels is not None:
            logs = [entry for entry in logs if entry.get(u'level') in levels]
        return logs

    def get_window_size(self):
        """Gets the window size

        @return: Window size
        """
        return self.driver.get_window_size()

    def set_window_size(self, width, height):
        """
        Sets the window width and height of the browser

        @return: None
        """
        self.driver.set_window_size(width, height)

    def quit(self):
        """Close driver and kill all associated displays

        """
        # Kill the driver

        def _quit():
            try:
                self.driver.quit()
            except Exception, err_driver:
                os.kill(self.driver_pid, signal.SIGKILL)
                raise
            finally:
                # Kill the display for this driver window
                try:
                    if self.display:
                        self.display.stop()
                except Exception, err_display:
                    os.kill(self.display_pid, signal.SIGKILL)
                    raise
        return self.execute_and_handle_webdriver_exceptions(_quit)
