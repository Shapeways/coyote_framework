"""
Webdriver Wrapper assertion module -- provides assertions for webdriverwrapper
"""
from coyote_framework.webdriver.webdriverwrapper.exceptions import WebDriverAssertionException

__author__ = 'justin'

from time import sleep


class WebDriverWrapperAssertion():
    """
    Provide advanced assertions to webdriverwrapper.
    """
    def __init__(self, driver_wrapper, timeout=30, step=1):
        self.timeout = timeout
        self.step = step
        self.driver_wrapper = driver_wrapper

    def fail(self, msg='Assertion was forced to fail. Check stacktrace to see where.'):
        """
         Raises a failed assertion exception; equivalent of 'assert False'

        @type msg:  str
        @param msg: a message to include in the assertion exception
        """
        raise WebDriverAssertionException.WebDriverAssertionException(self.driver_wrapper, msg)

    def spin_assert(self, assertion, failure_message='Failed Assertion', timeout=None):
        """
        Asserts that assertion function passed to it will return True,
        trying every 'step' seconds until 'timeout' seconds have passed.
        """
        timeout = self.timeout if timeout is None else timeout
        time_spent = 0
        while time_spent < timeout:
            try:
                assert assertion() is True
                return True
            except AssertionError:
                pass
            sleep(self.step)
            time_spent += 1
        raise WebDriverAssertionException.WebDriverAssertionException(self.driver_wrapper, failure_message)

    def webdriver_assert(self, assertion, failure_message='Failed Assertion'):
        """
        Assert the assertion, but throw a WebDriverAssertionException if assertion fails
        """
        try:
            assert assertion() is True
        except AssertionError:
            raise WebDriverAssertionException.WebDriverAssertionException(self.driver_wrapper, failure_message)

        return True

    def assert_eval(self, function_to_call, failure_message):
        """
        Calls the function with expectation of True
        """
        self.webdriver_assert(function_to_call, failure_message)

    def assert_true(self, value, failure_message='Expected value to be True, was: {}'):
        """
        Asserts that a value is true

        @type value:    bool
        @param value:   value to test for True
        """
        assertion = lambda: bool(value)
        self.webdriver_assert(assertion, unicode(failure_message).format(value))

    def assert_false(self, value, failure_message='Expected value to be False, was: {}'):
        """
        Asserts that a value is False

        @type value:    bool
        @param value:   value to test for False
        """
        assertion = lambda: not bool(value)
        self.webdriver_assert(assertion, unicode(failure_message).format(value))

    def assert_equals(self, actual_val, expected_val, failure_message='Expected values to be equal: "{}" and "{}"'):
        """
        Calls smart_assert, but creates its own assertion closure using
        the expected and provided values with the '==' operator
        """
        assertion = lambda: expected_val == actual_val
        self.webdriver_assert(assertion, unicode(failure_message).format(actual_val, expected_val))

    def assert_numbers_almost_equal(self, actual_val, expected_val, allowed_delta=0.0001,
                                    failure_message='Expected numbers to be within {} of each other: "{}" and "{}"'):
        """
        Asserts that two numbers are within an allowed delta of each other
        """
        assertion = lambda: abs(expected_val - actual_val) <= allowed_delta
        self.webdriver_assert(assertion, unicode(failure_message).format(allowed_delta, actual_val, expected_val))

    def assert_not_equal(self, actual_val, unexpected_val, failure_message='Expected values to differ: "{}" and "{}"'):
        """
        Calls smart_assert, but creates its own assertion closure using
        the expected and provided values with the '!=' operator
        """
        assertion = lambda: unexpected_val != actual_val
        self.webdriver_assert(assertion, unicode(failure_message).format(actual_val, unexpected_val))

    def assert_is(self, actual_val, expected_type, failure_message='Expected type to be "{1}," but was "{0}"'):
        """
        Calls smart_assert, but creates its own assertion closure using
        the expected and provided values with the 'is' operator
        """
        assertion = lambda: expected_type is actual_val
        self.webdriver_assert(assertion, unicode(failure_message).format(actual_val, expected_type))

    def assert_is_not(self, actual_val, unexpected_type,
                      failure_message='Expected type not to be "{1}," but was "{0}"'):
        """
        Calls smart_assert, but creates its own assertion closure using
        the expected and provided values with the 'is not' operator
        """
        assertion = lambda: unexpected_type is not actual_val
        self.webdriver_assert(assertion, unicode(failure_message).format(actual_val, unexpected_type))

    def assert_in(self, actual_collection_or_string, expected_value, failure_message='Expected "{1}" to be in "{0}"'):
        """
        Calls smart_assert, but creates its own assertion closure using
        the expected and provided values with the 'in' operator
        """
        assertion = lambda: expected_value in actual_collection_or_string
        self.webdriver_assert(assertion, unicode(failure_message).format(actual_collection_or_string, expected_value))

    def assert_not_in(self, actual_collection_or_string, unexpected_value,
                      failure_message='Expected "{1}" not to be in "{0}"'):
        """
        Calls smart_assert, but creates its own assertion closure using
        the expected and provided values with the 'not in' operator
        """
        assertion = lambda: unexpected_value not in actual_collection_or_string
        self.webdriver_assert(assertion, unicode(failure_message).format(actual_collection_or_string, unexpected_value))

    def assert_page_source_contains(self, expected_value, failure_message='Expected page source to contain: "{}"'):
        """
        Asserts that the page source contains the string passed in expected_value
        """
        assertion = lambda: expected_value in self.driver_wrapper.page_source()
        self.webdriver_assert(assertion, unicode(failure_message).format(expected_value))

    def assert_union(self, collection1, collection2,
                     failure_message='Expected overlap between collections: "{}" and "{}"'):
        """
        Asserts that the union of two sets has at least one member (collections share at least one member)
        """
        assertion = lambda: len(collection1 or collection2) > 0
        failure_message = unicode(failure_message).format(collection1, collection2)
        self.webdriver_assert(assertion, failure_message)

    def assert_no_union(self, collection1, collection2,
                        failure_message='Expected no overlap between collections: "{}" and "{}"'):
        """
        Asserts that the union of two sets is empty (collections are unique)
        """
        assertion = lambda: len(set(collection1).intersection(set(collection2))) == 0
        failure_message = unicode(failure_message).format(collection1, collection2)
        self.webdriver_assert(assertion, failure_message)

    def assert_subset(self, subset, superset, failure_message='Expected collection "{}" to be a subset of "{}'):
        """
        Asserts that a superset contains all elements of a subset
        """
        assertion = lambda: set(subset).issubset(set(superset))
        failure_message = unicode(failure_message).format(superset, subset)
        self.webdriver_assert(assertion, failure_message)