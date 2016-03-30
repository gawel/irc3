# -*- coding: utf-8 -*-
import os
import irc3
import logging
from irc3 import asyncio
from functools import partial
from irc3.plugins.command import Commands


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
            meth = partial(self.shell_command, v)
            meth.__name__ = k
            meth.__doc__ = '''Run $ %s
            %%%%%s
            ''' % (v, k)
            self.log.debug('Register command %s: $ %s', k, v)
            commands[k] = (predicates, asyncio.coroutine(meth))

    def shell_command(self, command, *args, **kwargs):
        f = asyncio.Future()
        env = os.environ.copy()
        env['IRC3_COMMAND'] = command
        task = asyncio.create_subprocess_shell(
            command, shell=True, env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT)
        task = self.context.create_task(task)
        task.add_done_callback(partial(self.wait, f))
        return f

    def wait(self, f, result):
        proc = result.result()
        task = self.context.create_task(proc.wait())
        task.add_done_callback(partial(self.read, f, proc))

    def read(self, f, proc, result):
        task = self.context.create_task(proc.stdout.read())
        task.add_done_callback(partial(self.send, f))

    def send(self, f, result):
        lines = result.result()
        f.set_result(lines.split('\n'))
