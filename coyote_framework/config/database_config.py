from coyote_framework.config.abstract_config import ConfigBase


class DatabaseConfig(ConfigBase):

    def __init__(self):
        database = target_database if target_database else 'database'
        super(DatabaseConfig, self).__init__(database)
