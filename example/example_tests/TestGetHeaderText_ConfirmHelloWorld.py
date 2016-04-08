from coyote_framework.testing.coyote_test import CoyoteTest
from example.example_app.config.example_config import ExampleConfig
from coyote_framework.drivers.coyote_driverfactory import driver_context
from example.example_app.page_objects.example_home_page import ExampleHomePage

__author__ = 'matt'


class TestGetHeaderText_ConfirmHelloWorld(CoyoteTest):
    """Test that we can load a page, retrieve some text, and verify its contents"""

    def setUp(self):
        super(TestGetHeaderText_ConfirmHelloWorld, self).setUp()
        self.config = ExampleConfig()

    def test_main(self):
        with driver_context() as driver:
            test = self.config.get('web_hostname')
            driver.visit(test)
            hp = ExampleHomePage(driver_wrapper=driver)
            driver.assertion.assert_true(hp.is_page_loaded())
            text = hp.get_hello_world_text()
            driver.assertion.assert_equals(text, "Hello world")