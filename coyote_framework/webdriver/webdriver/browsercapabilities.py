from selenium.webdriver import DesiredCapabilities


def copy_and_update(dictionary, update):
    """Returns an updated copy of the dictionary without modifying the original"""
    newdict = dictionary.copy()
    newdict.update(update)
    return newdict


class Capabilities(dict):
    def __init__(self, *args):
        super(Capabilities, self).__init__()
        for dicts in args:
            self.update(dicts)

    def add(self, settings):
        """Alias for update to allow chaining"""
        self.update(settings)
        return self


class Browser():

    FIREFOX = {
        '23':   copy_and_update(DesiredCapabilities.FIREFOX, {'version': '23'}),
        '22':   copy_and_update(DesiredCapabilities.FIREFOX, {'version': '22'}),
        '21':   copy_and_update(DesiredCapabilities.FIREFOX, {'version': '21'}),
        '20':   copy_and_update(DesiredCapabilities.FIREFOX, {'version': '20'}),
        '19':   copy_and_update(DesiredCapabilities.FIREFOX, {'version': '19'}),
        '18':   copy_and_update(DesiredCapabilities.FIREFOX, {'version': '18'}),
        '17':   copy_and_update(DesiredCapabilities.FIREFOX, {'version': '17'}),
        '16':   copy_and_update(DesiredCapabilities.FIREFOX, {'version': '16'}),
        '15':   copy_and_update(DesiredCapabilities.FIREFOX, {'version': '15'}),
        '14':   copy_and_update(DesiredCapabilities.FIREFOX, {'version': '14'}),
        '13':   copy_and_update(DesiredCapabilities.FIREFOX, {'version': '13'}),
        '12':   copy_and_update(DesiredCapabilities.FIREFOX, {'version': '12'}),
        '11':   copy_and_update(DesiredCapabilities.FIREFOX, {'version': '11'}),
        '10':   copy_and_update(DesiredCapabilities.FIREFOX, {'version': '10'}),
        '9':    copy_and_update(DesiredCapabilities.FIREFOX, {'version': '9'}),
        '8':    copy_and_update(DesiredCapabilities.FIREFOX, {'version': '8'}),
        '7':    copy_and_update(DesiredCapabilities.FIREFOX, {'version': '7'}),
        '6':    copy_and_update(DesiredCapabilities.FIREFOX, {'version': '6'}),
        '5':    copy_and_update(DesiredCapabilities.FIREFOX, {'version': '5'}),
        '4':    copy_and_update(DesiredCapabilities.FIREFOX, {'version': '4'}),
        '3.6':  copy_and_update(DesiredCapabilities.FIREFOX, {'version': '3.6'}),
        '3.5':  copy_and_update(DesiredCapabilities.FIREFOX, {'version': '3.5'}),
        '3.0':  copy_and_update(DesiredCapabilities.FIREFOX, {'version': '3.0'})
    }

    IE = {
        '10': copy_and_update(DesiredCapabilities.INTERNETEXPLORER, {'version': '10'}),
        '9':  copy_and_update(DesiredCapabilities.INTERNETEXPLORER, {'version': '9'}),
        '8':  copy_and_update(DesiredCapabilities.INTERNETEXPLORER, {'version': '8'}),
        '7':  copy_and_update(DesiredCapabilities.INTERNETEXPLORER, {'version': '7'}),
        '6':  copy_and_update(DesiredCapabilities.INTERNETEXPLORER, {'version': '6'})
    }

    CHROME = {
        '28': copy_and_update(DesiredCapabilities.CHROME, {'version': '28'}),
        '27': copy_and_update(DesiredCapabilities.CHROME, {'version': '27'})
    }

    OPERA = {
        '12': copy_and_update(DesiredCapabilities.OPERA, {'version': '12'}),
        '11': copy_and_update(DesiredCapabilities.OPERA, {'version': '11'})
    }

    SAFARI = {
        '6': copy_and_update(DesiredCapabilities.SAFARI, {'version': '6'}),
        '5': copy_and_update(DesiredCapabilities.SAFARI, {'version': '5'})
    }


class Platform():

    WINDOWS = {
        '8':  {'platform': 'Windows 8'},
        '7':  {'platform': 'Windows 7'},
        'XP': {'platform': 'Windows XP'}
    }

    MAC = {
        '10.8': {'platform': 'OS X 10.8'},
        '10.6': {'platform': 'OS X 10.6'}
    }

    IOS = {
        '6':   {'platform': 'OSX 10.8', 'version': '6'},
        '5.1': {'platform': 'OSX 10.8', 'version': '5.1'},
        '5.0': {'platform': 'OSX 10.6', 'version': '5.0'},
        '4':   {'platform': 'OSX 10.8', 'version': '4'}
    }

    IPHONE = {
        '6':   copy_and_update(DesiredCapabilities.IPHONE, IOS['6']),
        '5.1': copy_and_update(DesiredCapabilities.IPHONE, IOS['5.1']),
        '5.0': copy_and_update(DesiredCapabilities.IPHONE, IOS['5.0']),
        '4':   copy_and_update(DesiredCapabilities.IPHONE, IOS['4'])
    }

    IPAD = {
        '6':   copy_and_update(DesiredCapabilities.IPAD, IOS['6']),
        '5.1': copy_and_update(DesiredCapabilities.IPAD, IOS['5.1']),
        '5.0': copy_and_update(DesiredCapabilities.IPAD, IOS['5.0']),
        '4':   copy_and_update(DesiredCapabilities.IPAD, IOS['4'])
    }

    ANDROID = {
        '4.0': {'platform': 'Linux', 'version': '4.0'}
    }

    ANROID_TABLET = {
        '4.0': copy_and_update(ANDROID['4.0'], {'device-type': 'tablet'})
    }
