from coyote_framework.config.abstract_config import ConfigBase


class TimeoutConfig(ConfigBase):

    def __init__(self):
        super(TimeoutConfig, self).__init__('timeout')