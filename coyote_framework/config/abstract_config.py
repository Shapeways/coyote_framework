from ConfigParser import ConfigParser
import json
import fnmatch
import os

__author__ = 'justin@shapeways.com'


TEST_RUN_SETTING_CONFIG = 'TEST_RUN_SETTING_CONFIG'
confg_dict = {}


class NullConfigAttribute(object):

    def __init__(self, description, default_value=None):
        self.description = description
        self.default_value = default_value


class ConfigBase(object):
    """The config base; do not inherit from ConfigParser because it is an old-style class"""

    def __init__(self, section):
        if section not in confg_dict.keys():
            self.section = section
            self.parser = ConfigParser()
            self._readall()
            confg_dict[section] = self
        else:
            this_config = confg_dict[section]
            self.section = section
            self.parser = this_config.parser

    def get(self, key):
        return self.parser.get(self.section, key)

    def getbool(self, key):
        return bool(self.parser.getboolean(self.section, key))

    def getint(self, key):
        return int(self.get(key))

    def getfloat(self, key):
        return float(self.get(key))

    def getjson(self, key):
        raw = self.get(key)
        if not raw:
            raw = '{}'
        return json.loads(raw)

    def _readall(self):
        """Read configs from all available configs. It will read files in the following order:

            1.) Read all default settings:

                These are located under: `<project_root>/config/*/default.cfg`

            2.) Read the user's config settings:

                This is located on the path: `~/.aftrc`

            3.) Read all config files specified by the config string in the environment variable TEST_RUN_SETTING_CONFIG

                A config string such as "browser.headless,scripts.no_ssh" will read paths:

                    `<project_root>/config/browser/headless.cfg`
                    `<project_root>/config/scripts/no_ssh.cfg`
        """
        # First priority -- read all default configs
        config_path = os.path.dirname(__file__)
        config_defaults = [os.path.join(dirpath, f)
                           for dirpath, dirnames, files in os.walk(config_path)
                           for f in fnmatch.filter(files, 'default.cfg')]

        # Second priority -- read the user overrides
        user_config = os.path.expanduser('~/.aftrc')

        # Third priority -- read the environment variable overrides
        override_filenames = []
        if TEST_RUN_SETTING_CONFIG in os.environ:
            for test_config in os.environ[TEST_RUN_SETTING_CONFIG].split(','):
                override_filenames.append(test_config)

        all_configs = config_defaults + [user_config] + override_filenames
        return self.parser.read(all_configs)


def load_config_vars(target_config, source_config):
    """Loads all attributes from source config into target config

    @type target_config: TestRunConfigManager
    @param target_config: Config to dump variables into
    @type source_config: TestRunConfigManager
    @param source_config: The other config
    @return: True
    """
    # Overwrite all attributes in config with new config
    for attr in dir(source_config):
        # skip all private class attrs
        if attr.startswith('_'):
            continue
        val = getattr(source_config, attr)
        if val is not None:
            setattr(target_config, attr, val)