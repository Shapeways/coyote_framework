from coyote_framework.util.pageobjects.web import webobjects
from coyote_framework.webdriver.webdriverwrapper.support.locator import Locator

__author__ = 'matt'


class ExamplePage(webobjects.WebPage):

    page_id = None

    class locators(object):
        deferred_component = Locator('css', '[data-sw-deferred-component]', 'deferred component')

    def __init__(self, driver_wrapper, logger=None):
        super(ExamplePage, self).__init__(driver_wrapper=driver_wrapper, logger=logger)
        self.dw = driver_wrapper