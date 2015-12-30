from coyote_framework.config.host_config_manager import HostConfigManager

__author__ = 'justin'

import os


def ssh(cmd):
    cmd = "ssh %(sshHost)s \"%(cmd)s\"" % {
        'sshHost': HostConfigManager().get_host().hostname,
        'cmd':     cmd,
        }
    return cmd


def system(cmd):
    os.system(cmd)