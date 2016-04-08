from coyote_framework.config.abstract_config import ConfigBase


class ExampleConfig(ConfigBase):

    def __init__(self):
        super(ExampleConfig, self).__init__('example')