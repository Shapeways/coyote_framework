from coyote_framework.testing.coyote_test import CoyoteTest
from example.example_app.config.example_config import ExampleConfig
from coyote_framework.drivers.coyote_driverfactory import driver_context
from example.example_app.page_objects.example_home_page import ExampleHomePage

__author__ = 'matt'


class TestTriggerScan_ScanTriggeredSuccessfully(CoyoteTest):
    """Test that we can trigger a scan"""

    def setUp(self):
        super(TestTriggerScan_ScanTriggeredSuccessfully, self).setUp()
        self.config = ExampleConfig()

    def test_main(self):
        with driver_context() as driver:
            test = self.config.get('web_hostname')
            driver.visit(test)
            hp = ExampleHomePage(driver_wrapper=driver)
            assert hp.is_page_loaded()
