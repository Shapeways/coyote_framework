from coyote_framework.testing.coyote_test import CoyoteTest
from example.example_app.config.example_config import ExampleConfig
from coyote_framework.drivers.coyote_driverfactory import driver_context
from example.example_app.page_objects.example_home_page import ExampleHomePage

__author__ = 'matt'


class TestSubmitForm_ConfirmValues(CoyoteTest):
    """
    This test demonstrates how to interact w/ a form, as well as
    how to use components
    """

    def setUp(self):
        super(TestSubmitForm_ConfirmValues, self).setUp()
        self.config = ExampleConfig()

    def test_main(self):
        first_name = 'matt'
        last_name = 'boyle'
        with driver_context() as driver:
            # Visit the test page
            test = self.config.get('web_hostname')
            driver.visit(test)

            # Initialize the page object
            hp = ExampleHomePage(driver_wrapper=driver)
            driver.assertion.assert_true(hp.is_page_loaded())

            # Retrieve the LoginForm component.
            lf = hp.get_login_form_component()
            lf.enter_first_name(first_name)
            lf.enter_last_name(last_name)
            lf.click_submit()

            # Confirm that first and last names are displayed
            display_first_name = hp.get_first_name_display()
            display_last_name = hp.get_last_name_display()

            driver.assertion.assert_equals(display_first_name, first_name, 'first names did not match')
            driver.assertion.assert_equals(display_last_name, last_name, 'first names did not match')