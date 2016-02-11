import logging
import unittest
import datetime
import sys
from unittest import SkipTest

from coyote_framework.config.log_config import LogConfig


from coyote_framework.log import Logger
from coyote_framework.log.Logger import WARN, INFO, log

__author__ = 'mboyle'


class CoyoteTest(unittest.TestCase):

    webdriver_instances = []
    display_instances = []

    def setUp(self):
        log('----------------------------- SetUp -----------------------------')
        # Order is LIFO, put cleanups in reverse order
        self.addCleanup(lambda: self.cleanup_by_logging_end_statement())
        self.addCleanup(lambda: self.quit_drivers())
        self.addCleanup(lambda: self.stop_displays())

        self.test_id = self.__class__.__name__ + datetime.datetime.now().strftime("-%Y%m%d-%H%M%S")
        self.is_passed = False

        log_config = LogConfig()
        # set log levels
        selenium_logger = logging.getLogger('easyprocess')
        selenium_logger.setLevel(log_config.getint('default_third_party_logging_level'))

        selenium_logger = logging.getLogger('pyvirtualdisplay')
        selenium_logger.setLevel(log_config.getint('default_third_party_logging_level'))

        selenium_logger = logging.getLogger('pyvirtualdisplay.abstractdisplay')
        selenium_logger.setLevel(log_config.getint('default_third_party_logging_level'))

        selenium_logger = logging.getLogger('paramiko.transport')
        selenium_logger.setLevel(log_config.getint('default_third_party_logging_level'))

        selenium_logger = logging.getLogger('requests')
        selenium_logger.setLevel(log_config.getint('default_third_party_logging_level'))

        # configure testing logger
        self.logger = Logger.get()
        log('Beginning test {}'.format(self.test_id))

        # Create a data class to use for storing data
        class data(object):
            """Data object for saving data to"""

        self.data = data()

    def end_setup(self):
        """Ends the setup part of the test

        @return: None
        """
        log('----------------------------- RunningTest -----------------------------')

    def _skip(self, with_warn=True):
        if with_warn:
            log('Skipped test {}'.format(self.test_id), WARN)
        else:
            log('Skipped test {}'.format(self.test_id))
        raise SkipTest

    def set_passed(self, passed=True):
        self.is_passed = passed

    def quit_drivers(self):
        log('Quitting WebDriver')
        for driver in self.webdriver_instances:
            try:
                driver.quit()
            except Exception, e:
                log('Could not quit the driver ({})'.format(e), INFO)
                pass

    def stop_displays(self):
        for display in self.display_instances:
            try:
                display.stop()
            except Exception, e:
                log('Could not quit the display ({})'.format(display), INFO)

    def cleanup_by_logging_end_statement(self):
        log('Ending test {}'.format(self.test_id))

    def check_for_and_set_current_result(self):
        """Checks for currently handled exceptions and if there are none, return true; false if there are exceptions in
        the stacktrace

        """
        exceptions = sys.exc_info()
        no_exceptions_condition = (None, None, None)  # should get a tuple with null values if no exceptions
        if exceptions == no_exceptions_condition:
            self.set_passed(passed=True)
        else:
            self.set_passed(passed=False)

    def tearDown(self):
        log('----------------------------- TearDown -----------------------------')
        self.check_for_and_set_current_result()
        log('TEST PASSED' if self.is_passed else 'TEST FAILURE')
