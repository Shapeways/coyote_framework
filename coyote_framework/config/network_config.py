from coyote_framework.config.abstract_config import ConfigBase

class NetworkConfig(ConfigBase):

    def __init__(self):
        super(NetworkConfig, self).__init__('network')