from coyote_framework.util.pageobjects.web.webobjects import DormantWebComponent
from coyote_framework.webdriver.webdriverwrapper.support.locator import Locator
from example.example_app.page_objects.example_page import ExamplePage

__author__ = 'matt'

FOLLOW_PAGE = 'follow_page'


class ExampleFollowPage(ExamplePage):

    login_form = DormantWebComponent()

    class locators(ExamplePage.locators):
        find_me = Locator('css', '.find-me', 'find the main text')
        go_back_link = Locator('css', '.go-back', 'go back link')

    def __init__(self, driver_wrapper, logger=None):
        super(ExampleFollowPage, self).__init__(driver_wrapper=driver_wrapper, logger=logger)

    def is_page_loaded(self):
        """Test that Home page is loaded"""
        return self.dw.is_present(self.locators.find_me)

    def click_go_back_link(self):
        self.dw.find(self.locators.go_back_link).click()