from coyote_framework.testing.coyote_test import CoyoteTest
from example.example_app.config.example_config import ExampleConfig
from coyote_framework.drivers.coyote_driverfactory import driver_context
from example.example_app.page_objects.example_follow_page import ExampleFollowPage
from example.example_app.page_objects.example_home_page import ExampleHomePage

__author__ = 'matt'


class TestFollowLink_YouFollowedItGood(CoyoteTest):
    """
    Test that we can load a page, click a link,
    Instantiate a page object, click another link.

    You're really doin' it now, kid.  Complex shit.
    """

    def setUp(self):
        super(TestFollowLink_YouFollowedItGood, self).setUp()
        self.config = ExampleConfig()

    def test_main(self):
        with driver_context() as driver:
            test = self.config.get('web_hostname')
            driver.visit(test)
            hp = ExampleHomePage(driver_wrapper=driver)
            driver.assertion.assert_true(hp.is_page_loaded())

            # Let's go to another page.
            # Notice how we interact with hp, then instantiate fp after we land on it
            hp.click_follow_me()
            fp = ExampleFollowPage(driver_wrapper=driver)
            driver.assertion.assert_true(fp.is_page_loaded())

            # Now. let's go back to the home page
            # Notice that we re-instantiate hp, as the original hp now has a stale DOM
            fp.click_go_back_link()
            hp = ExampleHomePage(driver_wrapper=driver)
            driver.assertion.assert_true(hp.is_page_loaded())

