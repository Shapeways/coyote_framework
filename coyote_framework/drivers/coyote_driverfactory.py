import os
import datetime
import logging
import socket
import time
import urllib2

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import DesiredCapabilities
from pyvirtualdisplay import Display
from coyote_framework.config.constants_config import ConstantsConfig
from coyote_framework.log.Logger import log

from coyote_framework.config.browser_config import BrowserConfig
from coyote_framework.util.apps.randomwords import words
from coyote_framework.mixins.filesystem import create_directory
from coyote_framework.config.testrun_config import TestrunConfig
from coyote_framework.util.apps.polling import polling
from coyote_framework.mixins import timer
from coyote_framework.webdriver.webdriver import driverfactory
from coyote_framework.drivers.coyote_driver import CoyoteDriver
from coyote_framework.webdriver.webdriver.driverfactory import DriverFactory
from coyote_framework.webdriver.webdriverwrapper.WebDriverWrapper import quitting, BROWSER_LOG_LEVEL_SEVERE


__author__ = 'justin@shapeways.com'


def get_firefox_profile():
    # TODO: update this so that it is not browser-specific
    constants_config = ConstantsConfig()
    profile_directory = os.path.join(constants_config.get('webdriver_dir'), 'firefox', 'profile', 'tmp')
    create_directory(profile_directory)


    ffprofile = webdriver.FirefoxProfile(profile_directory)

    log_dir = os.path.join(constants_config.get('logs_dir'), 'webdriver')
    create_directory(log_dir)

    log_path = os.path.join(log_dir, '{}_{}.log'.format(datetime.datetime.now().isoformat('_'), words.random_word()))
    log('Selenium log file: {}'.format(log_path))

    # Accept firefox profiles
    ffprofile.set_preference('webdriver.log.file', log_path)
    return ffprofile


def get_firefox_binary():
    """Gets the firefox binary

    @rtype: FirefoxBinary
    """
    browser_config = BrowserConfig()
    constants_config = ConstantsConfig()
    log_dir = os.path.join(constants_config.get('logs_dir'), 'firefox')
    create_directory(log_dir)

    log_path = os.path.join(log_dir, '{}_{}.log'.format(datetime.datetime.now().isoformat('_'), words.random_word()))
    log_file = open(log_path, 'w')
    log('Firefox log file: {}'.format(log_path))

    binary = FirefoxBinary(log_file=log_file)

    return binary


def _log_fail_callback(driver, *args, **kwargs):
    """Raises an assertion error if the page has severe console errors

    @param driver: ShapewaysDriver
    @return: None
    """

    try:
        logs = driver.get_browser_log(levels=[BROWSER_LOG_LEVEL_SEVERE])
        failure_message = 'There were severe console errors on this page: {}'.format(logs)
        failure_message = failure_message.replace('{', '{{').replace('}', '}}')  # Escape braces for error message
        driver.assertion.assert_false(
            logs,
            failure_message=failure_message
        )
    except (urllib2.URLError, socket.error, WebDriverException):
        # The session has ended, don't check the logs
        pass


@timer.time_this_function(datadog_key='function:new_driver')
def new_driver():
    logger = logging.getLogger(__name__)
    browser_config = BrowserConfig()

    profile = get_firefox_profile()

    # TODO 1/2/15: put the capabilities somewhere better
    kwargs = dict()

    if browser_config.getbool('use_remote'):
        kwargs.update({
            'command_executor': browser_config.get('remote_command_executor'),
            'desired_capabilities': DesiredCapabilities.FIREFOX
        })
        kwargs['desired_capabilities'].update({'unexpectedAlertBehaviour': 'ignore'})  # Ignore unexpected alerts

        browser_name = driverfactory.REMOTE
    else:
        # Make sure correct Firefox version is installed
        binary = get_firefox_binary()

        kwargs.update({
            'firefox_profile': profile,
            'firefox_binary': binary
        })
        logger.debug('Driver profile is located at: {}'.format(profile.path))
        logger.debug('Driver binary is located at: {}'.format(binary._start_cmd))

        browser_name = driverfactory.FIREFOX

    try:
        driver = DriverFactory().new_driver(browser_name=browser_name,**kwargs)
    except WebDriverException, e:
        try:
            logger.critical('WebDriver could not start due to an error: {}'.format(e))
            if 'load the profile' in e.msg:
                logger.critical('There was an error loading the driver profile! Gathering debugging information...')

                profile_dir = profile.path
                logger.critical('Profile path is: {}'.format(profile_dir))

                profile_exists = os.path.exists(profile_dir)
                logger.critical('Profile path exists on filesystem: {}'.format(profile_exists))

                if profile_exists:
                    contents = os.listdir(profile_dir)
                    logger.critical('Profile contents are: {}'.format(contents))
        except:
            pass
        raise

    return driver


def new_driver_wrapper(startup_url=None):
    logger = logging.getLogger(__name__)
    browser_config = BrowserConfig()

    display = None
    if browser_config.getbool('use_headless_browser') and not browser_config.getbool('use_remote'):
        display = Display(visible=0, size=(1280, 1024))
        display.start()
        display_pid = display.pid

        def process_exists(pid):
            try:
                os.kill(pid, 0)
            except OSError:
                return False
            else:
                return True

        polling.poll(
            lambda: display.is_alive(),
            timeout=60,
            exception_message='Display was not alive; process was: {}'.format(display_pid),
            ontimeout=(
                lambda: logger.critical('Display process {} exists: {}'.format(
                    display_pid,
                    process_exists(display_pid))
                ),
            )
        )

        polling.poll(
            lambda: display.is_started,
            timeout=60,
            exception_message='Display was alive but not started; process was: {}'.format(display_pid)
        )

        # TODO: Is there a better condition we can check here?
        time.sleep(1.5)

    driver = new_driver()

    logging.getLogger(__name__).info('Browser successfully launched')

    action_callbacks = []
    # Fail if there are errors in the console
    if TestrunConfig().getbool('fail_on_console_errors'):
        action_callbacks.append(_log_fail_callback)

    driver_wrapper = CoyoteDriver(driver=driver, display=display, options={
        'timeout': 40,
        'page_load_timeout': 45,
        'ignore_page_load_timeouts': True,  # Prevent page timeouts from breaking out tests
        'action_callbacks': action_callbacks
    })
    driver.set_window_size(*(1280, 1024))
    return driver_wrapper


def driver_context(startup_url=None, *args, **kwargs):
    return quitting(new_driver_wrapper(startup_url))
