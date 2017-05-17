from coyote_framework.config.abstract_config import ConfigBase


class DatabaseConfig(ConfigBase):
    section = 'database' #specify what default section to use
    def __init__(self):
        super(DatabaseConfig, self).__init__(self.section) #not actually necessary


