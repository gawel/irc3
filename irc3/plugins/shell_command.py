# -*- coding: utf-8 -*-
import os
import irc3
import logging
import subprocess
from functools import partial
from irc3.plugins.command import Commands


def shell_command(context, command, *args, **kwargs):
    env = os.environ.copy()
    env['IRC3_COMMAND'] = command
    try:
        lines = subprocess.check_output(command, shell=True, env=env)
        for line in lines.split('\n'):
            yield line
    except Exception as e:
        context.log.exception(e)
        yield '%s' % e


@irc3.plugin
class ShellCommand(object):

    def __init__(self, context):
        self.log = logging.getLogger(__name__)
        self.context = context
        self.config = self.context.config[__name__]
        commands = self.context.get_plugin(Commands)
        predicates = {}
        for k, v in self.config.items():
            if v.startswith('#'):
                continue
            meth = partial(shell_command, self.context, v)
            meth.__name__ = k
            meth.__doc__ = '''Run $ %s
            %%%%%s
            ''' % (v, k)
            self.log.debug('Register command %s: $ %s', k, v)
            commands[k] = (predicates, meth)
