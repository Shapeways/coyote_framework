from config.abstract_config import ConfigBase


class NetworkConfig(ConfigBase):

    def __init__(self):
        super(NetworkConfig, self).__init__('network')