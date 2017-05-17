from ConfigParser import ConfigParser
import json
import fnmatch
import os
import sys

__author__ = 'justin@shapeways.com'


TEST_RUN_SETTING_CONFIG = 'TEST_RUN_SETTING_CONFIG'
config_dict = {}


class NullConfigAttribute(object):

    def __init__(self, description, default_value=None):
        self.description = description
        self.default_value = default_value


class ConfigBase(object):
    """The config base; do not inherit from ConfigParser because it is an old-style class"""


    def __new__(cls,section=None):
        '''
        Checks config_dict for pre-existence of instance for same section
        @param section: config section to check for existence, also checks cls.section if it exists
        @return: new or old instance of configbase or subclass
        '''

        inst_section = section if section else cls.section if hasattr(cls,'section') else None
        if inst_section in config_dict.keys():
            return config_dict[inst_section]
        else:
            return super(ConfigBase, cls).__new__(cls)

    def __init__(self, section=None):
        '''
        Sets up instance and will store it in config_dict if not there already
        For compatibility reasons, will also copy some attributes from config_dict
        @param section: section for this config. Deprecated (probably)
        @return:
        '''
        inst_section = section if section else self.section if hasattr(self,'section') else None
        if inst_section not in config_dict.keys():
            self.inherited_config_path = os.path.dirname(sys.modules[self.__class__.__module__].__file__) #TODO: works for subclasses, but not for other calls to coyote_framework lib
            self.section = inst_section
            self.parser = ConfigParser()
            self._readall()
            config_dict[inst_section] = self
        else:
            self.section = inst_section
            self.parser = config_dict[inst_section].parser
            self.inherited_config_path = config_dict[inst_section].inherited_config_path

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

                OR a config string such as "<project_root>/config/browser/headless.cfg" will load that path directly
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
                if os.path.exists(test_config):             #is this a file path
                   override_filenames.append(test_config)
                elif "." in test_config and not test_config.endswith('.cfg'):                    #else it might be in xxxx.yyyy format
                    config_parts = test_config.split('.')
                    config_parts[-1]+='.cfg' #add file ext to last part, which should be file
                    filename = os.path.join(self.inherited_config_path, *config_parts) #TODO: works for subclasses but not other access from coyote_framework
                    override_filenames.append(filename)
                else:                                       #else unknown, might throw exception here
                    pass


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
