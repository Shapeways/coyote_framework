from coyote_framework.util.pageobjects.web.webobjects import DormantWebComponent
from coyote_framework.webdriver.webdriverwrapper.support.locator import Locator
from example.example_app.page_objects.components.login_form import LoginForm
from example.example_app.page_objects.example_page import ExamplePage

__author__ = 'matt'

HOME_PAGE = 'home_page'


class ExampleHomePage(ExamplePage):

    login_form = DormantWebComponent()

    class locators(ExamplePage.locators):
        hello_world = Locator('css', '.hello-world', 'hello world title')
        follow_me_link = Locator('css', '.follow', 'follow me link')
        unhide_button = Locator('css', '#unhide', 'unhide button')
        hidden_div = Locator('css', '.hidden-div', 'hidden div')
        display_firstname = Locator('css', '.display-firstname', 'first name display')
        display_lastname = Locator('css', '.display-lastname', 'last name display')

    def __init__(self, driver_wrapper, logger=None):
        super(ExampleHomePage, self).__init__(driver_wrapper=driver_wrapper, logger=logger)

    def is_page_loaded(self):
        """Test that Home page is loaded"""
        return self.dw.is_present(self.locators.hello_world)

    def get_login_form_component(self):
        """Initializes and returns the login form component

        @rtype: LoginForm
        @return: Initialized component
        """
        self.dw.wait_until(
            lambda: self.dw.is_present(LoginForm.locators.form),
            failure_message='login form was never present so could not get the model '
                            'upload form component'
        )

        self.login_form = LoginForm(
            parent_page=self,
            element=self.dw.find(LoginForm.locators.form),
        )
        return self.login_form

    def get_hello_world_text(self):
        return self.dw.find(self.locators.hello_world).text()

    def click_see_me_button(self):
        self.dw.find(self.locators.unhide_button).click()

    def click_follow_me(self):
        self.dw.find(self.locators.follow_me_link).click()

    def confirm_text_visible(self, timeout=30):
        self.dw.wait_until_visibility_of(self.locators.hidden_div, timeout=timeout)

    def get_first_name_display(self):
        return self.dw.find(self.locators.display_firstname).text()

    def get_last_name_display(self):
        return self.dw.find(self.locators.display_lastname).text()