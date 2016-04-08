from coyote_framework.util.pageobjects.web.webobjects import WebComponent
from coyote_framework.webdriver.webdriverwrapper.support.locator import Locator

__author__ = 'matt'


class LoginForm(WebComponent):

    class locators(object):
        form = Locator('css', '.login-example', 'login form')

    def __init__(self, parent_page=None, element=None):
        super(LoginForm, self).__init__(parent_page=parent_page, element=element)

    def fill_out_form(self, first, last):
        pass

    def click_submit(self):
        pass
