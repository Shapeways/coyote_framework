from coyote_framework.testing.coyote_test import CoyoteTest
from example.example_app.config.example_config import ExampleConfig
from coyote_framework.drivers.coyote_driverfactory import driver_context
from example.example_app.page_objects.example_home_page import ExampleHomePage

__author__ = 'matt'


class TestClickButton_ShowText(CoyoteTest):
    """
    This test demonstrates how the webdriverwrapper waits can be used.

    First, we visit a page w/ a hidden div.  We try to confirm that we can see
    the text, but it's not yet visible, so this fails.  Then, we click a button
    which makes the text visible, and then successfully confirm we can see the text.
    """

    def setUp(self):
        super(TestClickButton_ShowText, self).setUp()
        self.config = ExampleConfig()

    def test_main(self):
        with driver_context() as driver:
            # Visit the test page
            test = self.config.get('web_hostname')
            driver.visit(test)

            # Initialize the page object
            hp = ExampleHomePage(driver_wrapper=driver)
            driver.assertion.assert_true(hp.is_page_loaded())

            # Demonstrate a failure of confirm_text_visible: we can't see it, because it's
            # currently set to display: none;
            try:
                hp.confirm_text_visible(timeout=5)
            except:
                print "Yep, can't see anything"

            # Click the button to expose the text, then try to read it again
            # This call succeeds.
            hp.click_see_me_button()
            hp.confirm_text_visible(timeout=5)