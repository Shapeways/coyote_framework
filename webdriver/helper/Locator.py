__author__ = 'mboyle'

class Locator(dict):
    """
    Storage container for webdriver locators.  Provides .'ed access to dictionary
    """
    def dumpData(self):
        for key, value in self.iteritems():
            print key, ":", str(value)

    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        else:
            raise AttributeError('Locator object has no attribute "%s"' % attr)
