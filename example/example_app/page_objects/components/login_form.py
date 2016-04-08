from coyote_framework.util.pageobjects.web.webobjects import WebComponent
from coyote_framework.webdriver.webdriverwrapper.support.locator import Locator

__author__ = 'matt'


class LoginForm(WebComponent):

    class locators(object):
        form = Locator('css', '.login-example', 'login form')
        first_name = Locator('css', '[name=fname]', 'first name input')
        last_name = Locator('css', '[name=lname]', 'last name input')
        submit_button = Locator('css', '.submit-button', 'submit button')

    def __init__(self, parent_page=None, element=None):
        super(LoginForm, self).__init__(parent_page=parent_page, element=element)

    def enter_first_name(self, fname):
        """
        @type fname: str
        @param fname: first name
        @return:
        """
        self.driver_wrapper.find(self.locators.first_name).set(fname)

    def enter_last_name(self, lname):
        """
        @type fname: str
        @param fname: first name
        @return:
        """
        self.driver_wrapper.find(self.locators.last_name).set(lname)

    def click_submit(self):
        self.driver_wrapper.find(self.locators.submit_button).click()
