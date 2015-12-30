__author__ = 'justin'

import datetime
import os

class ScreenshotTaker():

    def __init__(self, driver):
        self.driver = driver

    def take(self):
        screenshot_dir = os.path.join(os.path.dirname(__file__), '../../screenshots')
        if not os.path.exists(screenshot_dir):
            os.mkdir(screenshot_dir)
        return self.driver.save_screenshot(os.path.join(screenshot_dir, datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")+'.png'))