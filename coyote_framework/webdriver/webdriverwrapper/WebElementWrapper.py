"""
Module representing the web element wrapper
"""
from httplib import BadStatusLine
import logging
import re

__author__ = 'justin'

from selenium.common.exceptions import StaleElementReferenceException, ElementNotVisibleException, \
    MoveTargetOutOfBoundsException, TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from coyote_framework.webdriver.webdriverwrapper.exceptions import WebElementDoesNotExist, StaleWebElementException, WebElementNotVisibleException, \
    WebDriverTimeoutException


class WebElementWrapper():
    """
    WebElementWrapper class -- wraps selenium webelement to operate with webdriverwrapper
    """
    def __init__(self, driver_wrapper, locator, element=None, search_object=None):
        """
        @type driver_wrapper: WebDriverWrapper
        """
        self.driver_wrapper = driver_wrapper
        self.driver = driver_wrapper.driver
        self.locator = locator
        self.element = element
        self.search_object = search_object  # WebDriverWrapper of WebElementWrapper instance used to find the element

    def __str__(self):
        """
        Returns string representation of WebElementWrapper
        """
        message = "<WebElementWrapper: "

        try:
            REPR_HTML_SOURCE_LENGTH = 60
            REPR_HTML_SOURCE_TRAILING = '...'

            outer_html = self.get_attribute('outerHTML')
            if len(outer_html) > REPR_HTML_SOURCE_LENGTH + len(REPR_HTML_SOURCE_TRAILING):
                # Html source is too long
                outer_html = outer_html[:REPR_HTML_SOURCE_LENGTH] + REPR_HTML_SOURCE_TRAILING

            message += '"{}" '.format(outer_html)
            message += " located at {}".format(self.location())
        except Exception:
            message += ' -- (properties omitted)'
        finally:
            message += ">"
        return message

    def __repr__(self):
        """
        Implement __repr__ by calling __str__
        """
        return self.__str__()

    def get_width(self):
        """
        Returns the width of the element

        @return: Width of the element
        """
        return self.element.size['width']

    def get_height(self):
        """
        Returns the height of the element

        @return: Height of the element
        """
        return self.element.size['height']

    def wrap_element(self, element):
        """
        Wraps a webelement object in a webelementwrapper

        @type element:  selenium.webdriver.webelement
        @param element: the element to wrap

        @rtype:         WebWelementWrapper
        @return:        A WebelementWrapper contining the input element

        """
        self.element = element
        return self

    def clear(self):
        """
        Clears the field represented by this element

        @rtype:     WebElementWrapper
        @return:    Returns itself
        """
        def clear_element():
            """
            Wrapper to clear element
            """
            return self.element.clear()
        self.execute_and_handle_webelement_exceptions(clear_element, 'clear')
        return self

    def delete_content(self, max_chars=100):
        """
        Deletes content in the input field by repeatedly typing HOME, then DELETE

        @rtype:     WebElementWrapper
        @return:    Returns itself
        """
        def delete_content_element():
            chars_deleted = 0
            while len(self.get_attribute('value')) > 0 and chars_deleted < max_chars:
                self.click()
                self.send_keys(Keys.HOME)
                self.send_keys(Keys.DELETE)
                chars_deleted += 1

        self.execute_and_handle_webelement_exceptions(delete_content_element, 'delete input contents')
        return self

    def click(self, force_click=False):
        """
        Clicks the element

        @type force_click:  bool
        @param force_click: force a click on the element using javascript, skipping webdriver

        @rtype:             WebElementWrapper
        @return:            Returns itself
        """
        js_executor = self.driver_wrapper.js_executor

        def click_element():
            """
            Wrapper to call click
            """
            return self.element.click()

        def force_click_element():
            """
            Javascript wrapper to force_click the element
            """
            js_executor.execute_template('clickElementTemplate', {}, self.element)
            return True

        if force_click:
            self.execute_and_handle_webelement_exceptions(force_click_element, 'click element by javascript')
        else:
            self.execute_and_handle_webelement_exceptions(click_element, 'click')

        return self

    def get_value(self):
        """Gets the value of a select or input element

        @rtype: str
        @return: The value of the element
        @raise: ValueError if element is not of type input or select, or has multiple selected options
        """
        def get_element_value():
            if self.tag_name() == 'input':
                return self.get_attribute('value')
            elif self.tag_name() == 'select':
                selected_options = self.element.all_selected_options
                if len(selected_options) > 1:
                    raise ValueError(
                        'Select {} has multiple selected options, only one selected '
                        'option is valid for this method'.format(self)
                    )
                return selected_options[0].get_attribute('value')
            else:
                raise ValueError('Can not get the value of elements or type "{}"'.format(self.tag_name()))

        return self.execute_and_handle_webelement_exceptions(get_element_value, name_of_action='get value')

    def get_attribute(self, name):
        """
        Retrieves specified attribute from WebElement

        @type name:     str
        @param name:    Attribute to retrieve

        @rtype:         str
        @return:        String representation of the attribute
        """
        def get_attribute_element():
            """
            Wrapper to retrieve element
            """
            return self.element.get_attribute(name)
        return self.execute_and_handle_webelement_exceptions(get_attribute_element, 'get attribute "' + str(name) + '"')

    def get_parent(self):
        """
        Retrieves the parent of the element

        @rtype:     WebElementWrapper
        @return:    Returns a WebElementWrapper representing the parent of this WebElementWrapper
        """
        return self.find('xpath=..')

    def get_first_selected_option(self):
        """
        Get the first selected option
        @return: Returns a WebElementWrapper representing the first selected option
        @rtype: WebElementWrapper
        """
        return Select(self.element).first_selected_option

    def is_displayed(self):
        """
        Indicates whether or not the element is displayed

        @rtype:     bool
        @return:    True if element is displayed, False if not.
        """
        def is_displayed_element():
            """
            Wrapper to determine display status
            """
            return self.element.is_displayed()
        return self.execute_and_handle_webelement_exceptions(is_displayed_element, 'check if displayed')

    def is_on_screen(self):
        """Tests if the element is within the viewport of the screen (partially hidden by overflow will return true)

        @return: True if on screen, False otherwise
        """
        width = self.get_width()
        height = self.get_height()
        loc = self.location()
        el_x_left = loc['x']
        el_x_right = el_x_left + width
        el_y_top = loc['y']
        el_y_bottom = el_y_top + height

        screen_size = self.driver_wrapper.get_window_size()
        screen_x = screen_size['width']
        screen_y = screen_size['height']

        if (((el_x_left > 0 and el_x_right < screen_x) or (el_x_right > 0 and el_x_right <screen_x)) and
            ((el_y_top > 0 and el_y_top < screen_y) or (el_y_bottom > 0 and el_y_bottom > screen_y))
        ):
            return True
        return False

    def is_enabled(self):
        """
        Indicates whether or not the element is enabled

        @rtype:     bool
        @return:    True if element is enabled, False if not.
        """
        def is_enabled_element():
            """
            Wrapper to determine enabled status
            """
            return self.element.is_enabled()
        return self.execute_and_handle_webelement_exceptions(is_enabled_element, 'check if enabled')

    def is_selected(self):
        """
        Indicates whether or not the element is selected

        @rtype:     bool
        @return:    True if element is selected, False if not.
        """
        def is_selected_element():
            """
            Wrapper to determine selected status
            """
            return self.element.is_selected()
        return self.execute_and_handle_webelement_exceptions(is_selected_element, 'check if selected')

    def send_special_keys(self, value):
        """
        Send special keys such as <enter> or <delete>

        @rtype:     WebElementWrapper
        @return:    Self
        """
        def send_keys_element():
            """
            Wrapper to send keys
            """
            return self.element.send_keys(value)
        self.execute_and_handle_webelement_exceptions(send_keys_element, 'send keys')
        return self

    def send_keys(self, value):
        """
        Send keystrokes to web element

        @rtype:     WebElementWrapper
        @return:    Self
        """
        def send_keys_element():
            """
            Wrapper to send keys
            """
            return self.element.send_keys(value)
        self.execute_and_handle_webelement_exceptions(send_keys_element, 'send keys')
        return self

    def set(self, val, force_set=False):
        """
        Sets an input with a specified value; if force_set=True, will set through javascript if webdriver fails
        NOTE: if val is None, this function will interpret this to be an empty string

        @type val:          str
        @param val:         string to send to element
        @type force_set:    bool
        @param force_set:   Use javascript if True, webdriver if False
        """

        if val is None:
            val = ""

        self.click(force_click=True if force_set else False)
        self.clear()
        self.send_keys(val)
        actual = self.get_attribute('value')
        if val != actual:
            if force_set:
                js_executor = self.driver_wrapper.js_executor

                def force_set_element():
                    """
                    Wrapper to force_set element via javascript if needed
                    """
                    js_executor.execute_template('setValueTemplate', {'value': val}, self.element)
                    return True
                self.execute_and_handle_webelement_exceptions(force_set_element, 'set element by javascript')
            else:
                self.driver_wrapper.assertion.fail(
                    'Setting text field failed because final text did not match input value: "{}" != "{}"'.format(
                        actual,
                        val
                    )
                )
        return self

    def submit(self):
        """
        Submit a webe element

        @rtype:     WebElementWrapper
        @return:    Self
        """
        def submit_element():
            """
            Wrapper to submit element
            """
            return self.element.submit()
        self.execute_and_handle_webelement_exceptions(submit_element, 'send keys')
        return self

    def value_of_css_property(self, property_name):
        """
        Get value of CSS property for element

        @rtype:     str
        @return:    value of CSS property
        """
        def value_of_css_property_element():
            """
            Wrapper to get css property
            """
            return self.element.value_of_css_property(property_name)
        return self.execute_and_handle_webelement_exceptions(value_of_css_property_element, 'get css property "' +
                                                                                           str(property_name) + '"')

    def has_class(self, classname):
        """Test if an element has a specific classname

        @type classname: str
        @param classname: Classname to test for; cannot contain spaces
        @rtype: bool
        @return: True if classname exists; false otherwise
        """
        def element_has_class():
            """Wrapper to test if element has a class"""
            pattern = re.compile('(\s|^){classname}(\s|$)'.format(classname=classname))
            classes = self.element.get_attribute('class')
            matches = re.search(pattern, classes)

            if matches is not None:
                return True
            return False

        return self.execute_and_handle_webelement_exceptions(
            element_has_class,
            'check for element class "{}"'.format(classname)
        )

    def id(self):
        """
        Get the element ID

        @rtype:     str
        @return:    elemenet ID
        """
        def id_element():
            """
            Wrapper to get element ID
            """
            return self.element.id
        return self.execute_and_handle_webelement_exceptions(id_element, 'get id')

    def location(self):
        """
        Get the XY location of the element

        @rtype:     Location
        @return:    Location of element on screen
        """
        def location_element():
            """
            wrapper to retrieve element location
            """
            return self.element.location

        return self.execute_and_handle_webelement_exceptions(location_element, 'get location')

    def parent(self):
        """
        Get the parent of the element

        @rtype:     WebElementWrapper
        @return:    Parent of webelementwrapper on which this was invoked
        """
        def parent_element():
            """
            Wrapper to retrieve parent element
            """
            return WebElementWrapper(self.driver_wrapper, self.locator, self.element.parent)
        return self.execute_and_handle_webelement_exceptions(parent_element, 'get parent')

    def parent_element(self):
        """
        Get the parent of the element

        @rtype:     WebElementWrapper
        @return:    Parent of webelementwrapper on which this was invoked
        """
        def parent_element():
            """
            Wrapper to get parent element
            """
            parent = self.driver_wrapper.execute_script('return arguments[0].parentNode;', self.element)
            wrapped_parent = WebElementWrapper(self.driver_wrapper, '', parent)
            return wrapped_parent

        return self.execute_and_handle_webelement_exceptions(parent_element, 'get parent element')

    def size(self):
        """
        Get the size of the element

        @rtype:     dict
        @return:    Size of element
        """
        def size_element():
            """
            Wrapper to return size
            """
            return self.element.size
        return self.execute_and_handle_webelement_exceptions(size_element, 'get size')

    def tag_name(self):
        """
        Get the tag name of the element

        @rtype:     str
        @return:    tag name
        """
        def tag_name_element():
            """
            Wrapper to return tag name
            """
            return self.element.tag_name
        return self.execute_and_handle_webelement_exceptions(tag_name_element, 'get tag name')

    def text(self, force_get=False):
        """
        Get the text of the element

        @rtype:     str
        @return:    Text of the element
        """
        def text_element():
            """
            Wrapper to get text of element
            """
            return self.element.text

        def force_text_element():
            """Get text by javascript"""
            return self.driver_wrapper.js_executor.execute_template_and_return_result(
                'getElementText.js', {}, self.element
            )

        if force_get:
            return self.execute_and_handle_webelement_exceptions(force_text_element, 'get text by javascript')
        else:
            return self.execute_and_handle_webelement_exceptions(text_element, 'get text')

    def highlight(self):
        """
        Draws a dotted red box around the wrapped element using javascript

        @rtype:     WebElementWrapper
        @return:    Self
        """
        js_executor = self.driver_wrapper.js_executor
        def highlight_element():
            """
            Wrapper to highlight elements
            """
            location = self.element.location
            size = self.element.size
            js_executor.execute_template('elementHighlighterTemplate', {
                'x': str(location['x']),
                'y': str(location['y']),
                'width': str(size['width']),
                'height': str(size['height'])})
            return True
        self.execute_and_handle_webelement_exceptions(highlight_element, 'highlight')
        return self

    def set_attribute(self, name, value):
        """Sets the attribute of the element to a specified value

        @type name:     str
        @param name:    the name of the attribute
        @type value:    str
        @param value:   the attribute of the value
        """
        js_executor = self.driver_wrapper.js_executor
        def set_attribute_element():
            """
            Wrapper to set attribute
            """
            js_executor.execute_template('setAttributeTemplate', {
                'attribute_name': str(name),
                'attribute_value': str(value)}, self.element)
            return True
        self.execute_and_handle_webelement_exceptions(set_attribute_element,
                                                      'set attribute "' + str(name) + '" to "' + str(value) + '"')
        return self

    # TODO: a select method which checks that it is an option tag, gets the parent, then selects itself

    def select_option(self, value=None, text=None, index=None):
        """
        Selects an option by value, text, or index. You must name the parameter

        @type value:    str
        @param value:   the value of the option
        @type text:     str
        @param text:    the option's visible text
        @type index:    int
        @param index:   the zero-based index of the option

        @rtype:     WebElementWrapper
        @return:    self
        """
        def do_select():
            """
            Perform selection
            """
            return self.set_select('select', value, text, index)
        return self.execute_and_handle_webelement_exceptions(do_select, 'select option')

    def deselect_option(self, value=None, text=None, index=None):
        """
        De-selects an option by value, text, or index. You must name the parameter

        @type value:    str
        @param value:   the value of the option
        @type text:     str
        @param text:    the option's visible text
        @type index:    int
        @param index:   the zero-based index of the option

        @rtype:     WebElementWrapper
        @return:    self
        """
        def do_deselect():
            """
            Perform selection
            """
            return self.set_select('deselect', value, text, index)
        return self.execute_and_handle_webelement_exceptions(do_deselect, 'deselect option')

    def deselect_all(self):
        """
        Deselects all options of the select element

        @rtype:     WebElementWrapper
        @return:    self
        """
        def do_deselect_all():
            """
            Perform selection
            """
            return self.set_select('deselect all')
        return self.execute_and_handle_webelement_exceptions(do_deselect_all, 'deselect all')

    def set_select(self, select_or_deselect = 'select', value=None, text=None, index=None):
        """
        Private method used by select methods

        @type select_or_deselect:   str
        @param select_or_deselect:  Should I select or deselect the element
        @type value:                str
        @type value:                Value to be selected
        @type text:                 str
        @type text:                 Text to be selected
        @type index:                int
        @type index:                index to be selected

        @rtype:     WebElementWrapper
        @return:    Self
        """
        # TODO: raise exception if element is not select element

        if select_or_deselect is 'select':
            if value is not None:
                Select(self.element).select_by_value(value)
            elif text is not None:
                Select(self.element).select_by_visible_text(text)
            elif index is not None:
                Select(self.element).select_by_index(index)

        elif select_or_deselect is 'deselect':
            if value is not None:
                Select(self.element).deselect_by_value(value)
            elif text is not None:
                Select(self.element).deselect_by_visible_text(text)
            elif index is not None:
                Select(self.element).deselect_by_index(index)

        elif select_or_deselect is 'deselect all':
            Select(self.element).deselect_all()

        return self

    def checkbox_check(self, force_check=False):
        """
        Wrapper to check a  checkbox
        """
        if not self.get_attribute('checked'):
            self.click(force_click=force_check)

    def checkbox_uncheck(self, force_check=False):
        """
        Wrapper to uncheck a checkbox
        """
        if self.get_attribute('checked'):
            self.click(force_click=force_check)

    def is_checkbox_checked(self):
        """Tests if a checkbox is checked

        @rtype: bool
        @return: True if checked, false otherwise
        """
        return self.get_attribute('checked')

    def hover(self):
        """
        Hovers the element
        """
        def do_hover():
            """
            Perform hover
            """
            ActionChains(self.driver_wrapper.driver).move_to_element(self.element).perform()
        return self.execute_and_handle_webelement_exceptions(do_hover, 'hover')

    def find(self, locator, find_all=False, search_object=None, exclude_invisible=None, *args, **kwargs):
        """
        Find wrapper, invokes webDriverWrapper find with the current element as the search object

        @type locator:          webdriverwrapper.support.locator.Locator
        @param locator:         locator used in search
        @type find_all:         bool
        @param find_all:        should I find all elements, or just one?
        @type search_object:    WebElementWrapper
        @param search_object:   Used to override the starting point of the driver search

        @rtype:                 WebElementWrapper or list[WebElementWrapper]
        @return:                Either a single WebElementWrapper, or a list of WebElementWrappers
        """
        search_object = self.element if search_object is None else search_object
        return self.driver_wrapper.find(
            locator,
            find_all,
            search_object=search_object,
            exclude_invisible=exclude_invisible
        )

    def find_once(self, locator):
        """
        Find wrapper to run a single find

        @type locator:          webdriverwrapper.support.locator.Locator
        @param locator:         locator used in search
        @type find_all:         bool
        @param find_all:        should I find all elements, or just one?

        @rtype:                 WebElementWrapper or list[WebElementWrapper]
        @return:                Either a single WebElementWrapper, or a list of WebElementWrappers
        """
        params = []
        params.append(self.driver_wrapper.find_attempts)
        params.append(self.driver_wrapper.implicit_wait)

        self.driver_wrapper.find_attempts = 1
        self.driver_wrapper.implicit_wait = 0

        result = self.driver_wrapper._find_immediately(locator, self.element)

        # restore the original params
        self.driver_wrapper.implicit_wait = params.pop()
        self.driver_wrapper.find_attempts = params.pop()

        return result

    def find_all(self, locator):
        """
        Find wrapper, finds all elements

        @type locator:          webdriverwrapper.support.locator.Locator
        @param locator:         locator used in search

        @rtype:                 list
        @return:                A list of WebElementWrappers
        """
        return self.driver_wrapper.find(locator, True, self.element)

    def is_present(self, locator):
        """
        Tests to see if an element is present

        @type locator:          webdriverwrapper.support.locator.Locator
        @param locator:         locator used in search

        @rtype:                 bool
        @return:                True if present, False if not present
        """
        return self.driver_wrapper.is_present(locator, search_object=self.element)

    def is_stale(self):
        """Tests if the element is stale

        @rtype: bool
        @return: True if element is stale, false otherwise
        """
        try:
            # Calling any method forces a staleness check
            self.element.is_enabled()
            return False
        except StaleElementReferenceException as expected:
            return True

    def wait_until_stale(self, timeout=None):
        """
        Waits for the element to go stale in the DOM

        @type timeout:          int
        @param timeout:         override for default timeout

        @rtype:                 WebElementWrapper
        @return:                Self
        """
        timeout = timeout if timeout is not None else self.driver_wrapper.timeout

        def wait():
            """
            Wrapper to wait for element to be stale
            """
            WebDriverWait(self.driver, timeout).until(EC.staleness_of(self.element))
            return self

        return self.execute_and_handle_webelement_exceptions(wait, 'wait for staleness')

    def execute_and_handle_webelement_exceptions(self, function_to_execute, name_of_action):
        """
        Private method to be called by other methods to handle common WebDriverExceptions or throw
        a custom exception

        @type function_to_execute:      types.FunctionType
        @param function_to_execute:     A function containing some webdriver calls
        @type name_of_action:           str
        @param name_of_action:          The name of the action you are trying to perform for building the error message
        """
        if self.element is not None:
            attempts = 0
            while attempts < self.driver_wrapper.find_attempts+1:
                try:
                    attempts = attempts + 1
                    val = function_to_execute()
                    for cb in self.driver_wrapper.action_callbacks:
                        cb.__call__(self.driver_wrapper)
                    return val
                except StaleElementReferenceException:
                    self.element = self.driver_wrapper.find(self.locator, search_object=self.search_object).element
                except ElementNotVisibleException:
                    raise WebElementNotVisibleException.WebElementNotVisibleException(self,
                        'WebElement with locator: {} was not visible, so could not {}'.format(
                            self.locator, name_of_action))
                except MoveTargetOutOfBoundsException:
                    raise WebElementNotVisibleException.WebElementNotVisibleException(self,
                        'WebElement with locator: {} was out of window, so could not {}'.format(
                            self.locator, name_of_action))
                except TimeoutException:
                    raise WebDriverTimeoutException.WebDriverTimeoutException(
                        self.driver_wrapper, timeout=self.driver_wrapper.timeout, locator=self.locator,
                        msg='Timeout on action: {}'.format(name_of_action))
                except UnexpectedAlertPresentException:
                    msg = 'failed to parse message from alert'
                    try:
                        a = self.driver.switch_to_alert()
                        msg = a.text
                    finally:
                        raise UnexpectedAlertPresentException('Unexpected alert on page: {}'.format(msg))
                except BadStatusLine, e:
                    logging.getLogger(__name__).error('{} error raised on action: {} (line: {}, args:{}, message: {})'.format(
                        BadStatusLine.__class__.__name__,
                        name_of_action,
                        e.line,
                        e.args,
                        e.message
                    ))
                    raise

            raise StaleWebElementException.StaleWebElementException(self,
                'Cannot {} element with locator: {}; the reference to the WebElement was stale ({} attempts)'
                .format(name_of_action, self.locator, self.driver_wrapper.find_attempts))
        else:
            raise WebElementDoesNotExist.WebElementDoesNotExist(self,
                'Cannot {} element with locator: {}; it does not exist'.format(name_of_action, self.locator))