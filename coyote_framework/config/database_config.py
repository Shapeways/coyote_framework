from coyote_framework.config.abstract_config import ConfigBase


class DatabaseConfig(ConfigBase):

    def __init__(self):
        super(DatabaseConfig, self).__init__('database')


