from coyote_framework.config.abstract_config import ConfigBase


class LogConfig(ConfigBase):

    def __init__(self):
        super(LogConfig, self).__init__('log')