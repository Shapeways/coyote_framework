from coyote_framework.config.abstract_config import ConfigBase


class BrowserConfig(ConfigBase):

    def __init__(self):
        super(BrowserConfig, self).__init__('browser')


