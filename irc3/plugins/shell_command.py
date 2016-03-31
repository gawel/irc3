# -*- coding: utf-8 -*-
import os
import irc3
import logging
from irc3 import asyncio
from irc3.compat import text_type
from functools import partial
from irc3.plugins.command import Commands
__doc__ = '''
==========================================
:mod:`irc3.plugins.shell_command` Fifo plugin
==========================================

Allow to quickly add commands map to a shell command.
The bot will print stdout/stderr

..
    >>> from irc3.testing import IrcBot
    >>> from irc3.testing import ini2config

Usage::

    >>> config = ini2config("""
    ... [bot]
    ... includes =
    ...     irc3.plugins.shell_command
    ... [irc3.plugins.shell_command]
    ... myscript = /tmp/myscript
    ... # optional command configuration
    ... myscript.permission = runmyscrypt  # default permission is admin
    ... myscript.public = false  # default is true
    ... """)
    >>> bot = IrcBot(**config)

Then the uname command will be available::

    >>> bot.test(':gawel!user@host PRIVMSG #chan :!help myscript')
    PRIVMSG #chan :Run $ /tmp/myscript
    PRIVMSG #chan :!myscript [<args>...]

    >>> bot.test(':gawel!user@host PRIVMSG #chan :!myscript')

If the user provides some arguments then those will be available as an
environment var (to avoid shell injection) names ``IRC3_COMMAND_ARGS``
'''


@irc3.plugin
class Shell(object):

    requires = [Commands.__module__]

    def __init__(self, context):
        self.log = logging.getLogger(__name__)
        self.context = context
        self.config = self.context.config[__name__]
        commands = self.context.get_plugin(Commands)
        predicates = {'permission': 'admin'}
        for k, v in self.config.items():
            if v.startswith('#') or '.' in k:
                continue
            meth = partial(self.shell_command, v)
            meth.__name__ = k
            meth.__doc__ = '''Run $ %s
            %%%%%s [<args>...]
            ''' % (v, k)
            p = predicates.copy()
            for opt in ('permission', 'public'):
                opt_key = '%s.%s' % (k, opt)
                if opt_key in self.config:
                    p[opt] = self.config[opt_key]
            self.log.debug('Register command %s(%r): $ %s', k, p, v)
            commands[k] = (predicates, asyncio.coroutine(meth))

    def shell_command(self, command, mask, target, args, **kwargs):
        env = os.environ.copy()
        env['IRC3_COMMAND_ARGS'] = ' '.join(args['<args>'])
        proc = yield from asyncio.create_subprocess_shell(
            command, shell=True, env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT)
        yield from proc.wait()
        lines = yield from proc.stdout.read()
        if not isinstance(lines, text_type):
            lines = lines.decode('utf8')
        return lines.split(u'\n')
