import irc3
from irc3 import utils, asyncio
import re

__doc__ = '''
==================================================
:mod:`irc3.plugins.autocommand` Autocommand plugin
==================================================

This plugin allows to send IRC commands to the server after connecting.
This could be usable for authorization, cloaking, requesting invite to invite
only channel and other use cases.
It also allows to set delays between IRC commands via the ``/sleep`` command.

..
    >>> from irc3.testing import IrcBot
    >>> from irc3.testing import ini2config

Usage::

This example will authorize on Freenode:

    >>> config = ini2config("""
    ... [bot]
    ... includes =
    ...     irc3.plugins.autocommand
    ...
    ... autocommands =
    ...     PRIVMSG NickServ :IDENTIFY nick password
    ... """)
    >>> bot = IrcBot(**config)

Here's another, more complicated example:

    >>> config = ini2config("""
    ... [bot]
    ... includes =
    ...     irc3.plugins.autocommand
    ...
    ... autocommands =
    ...     AUTH user password
    ...     MODE {nick} +x
    ...     /sleep 2
    ...     PRIVMSG Q :INVITE #inviteonly
    ... """)
    >>> bot = IrcBot(**config)

It will authorize on QuakeNet, cloak and request an invite to ``#inviteonly``
after a 2 second delay.
'''


class SimpleCommand:

    def __init__(self, cmd):
        self.cmd = cmd

    @asyncio.coroutine
    def execute(self, bot):
        send_cmd = self.cmd.format(nick=bot.nick)
        bot.send_line(send_cmd)


class SleepCommand:

    SLEEP_RE = re.compile(r"^/sleep\s+(?P<time>[\d\.]+)\s*$", re.IGNORECASE)
    IS_SLEEP_RE = re.compile(r"/sleep\b", re.IGNORECASE)

    def __init__(self, time):
        if isinstance(time, (int, float)):
            self.time = time
        else:
            raise TypeError("Wrong type of argument")

    @classmethod
    def is_match(cls, test_str):
        return bool(cls.IS_SLEEP_RE.match(test_str))

    @classmethod
    def parse(cls, cmd_str):
        sleep_m = cls.SLEEP_RE.match(cmd_str)
        if sleep_m is not None:
            try:
                val = float(sleep_m.groupdict()['time'])
            except ValueError:
                raise ValueError("Wrong argument for /sleep command")
            else:
                return cls(val)
        else:
            raise ValueError("Wrong usage of /sleep command")

    @asyncio.coroutine
    def execute(self, bot):
        yield from asyncio.sleep(self.time, loop=bot.loop)


@irc3.plugin
class AutoCommand:

    requires = [
        'irc3.plugins.core',
    ]

    def __init__(self, bot):
        self.bot = bot
        cmds = utils.as_list(self.bot.config.get('autocommands', []))
        self.commands = [self.parse_command(cmd) for cmd in cmds]

    @staticmethod
    def parse_command(command):
        if not command:
            return

        if command.startswith('/'):
            if SleepCommand.is_match(command):
                return SleepCommand.parse(command)
            else:
                raise ValueError("Unknown command {cmd}".format(cmd=command))
        else:
            return SimpleCommand(command)

    def server_ready(self):
        # async deprecated since 3.4.4
        asyncio.ensure_future(self.execute_commands(), loop=self.bot.loop)

    @asyncio.coroutine
    def execute_commands(self):
        for command in self.commands:
            yield from command.execute(self.bot)
