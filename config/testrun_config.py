from coyote_framework.config.abstract_config import ConfigBase


class TestrunConfig(ConfigBase):

    def __init__(self):
        super(TestrunConfig, self).__init__('testrun')