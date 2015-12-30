import os
from selenium import webdriver


FIREFOX = 'firefox'
CHROME = 'chrome'
IE = 'ie'
OPERA = 'opera'
REMOTE = 'remote'
PHANTOMJS = 'phantomjs'


class DriverFactory(object):

    @staticmethod
    def new_driver(browser_name, *args, **kwargs):
        """Instantiates a new WebDriver instance, determining class by environment variables
        """
        if browser_name == FIREFOX:
            return webdriver.Firefox(*args, **kwargs)

        # elif options['local'] and options['browser_name'] == CHROME:
        #     return webdriver.Chrome(*args, **kwargs)
        #
        # elif options['local'] and options['browser_name'] == IE:
        #     return webdriver.Ie(*args, **kwargs)
        #
        # elif options['local'] and options['browser_name'] == OPERA:
        #     return webdriver.Opera(*args, **kwargs)

        elif browser_name == PHANTOMJS:
            executable_path = os.path.join(os.path.dirname(__file__), 'phantomjs/executable/phantomjs_64bit')
            driver = webdriver.PhantomJS(executable_path=executable_path, **kwargs)
            driver.set_window_size(1280, 800)  # Set a default because phantom needs it
            return driver

        else:  # remote
            driver = webdriver.Remote(*args, **kwargs)
            return driver