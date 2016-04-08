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
        first_name_input = Locator('css', '.')

    def __init__(self, driver_wrapper, logger=None):
        super(ExampleHomePage, self).__init__(driver_wrapper=driver_wrapper, logger=logger)

    def is_page_loaded(self):
        """Test that Home page is loaded"""
        return self.dw.is_present(self.locators.hello_world)

    def get_signup_form_component(self):
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

    def click_see_me_button(self):
        pass

    def verify_we_can_see_text(self):
        pass

    def click_follow_me(self):
        pass