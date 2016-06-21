import irc3
from irc3 import utils, asyncio
import re

__doc__ = '''
==================================================
:mod:`irc3.plugins.autocommand` Autocommand plugin
==================================================

Plugin allows send IRC commands after connecting to server. This could
be usable for authorization, cloaking, requesting invite to invite only channel
and other use cases. Also, plugin allows to set delay between IRC commands via
``/sleep`` command.

..
    >>> from irc3.testing import IrcBot

Usage::

This example will authorize you in FreeNode IRC network.

    >>> bot = IrcBot(autocommand=['PRIVMSG NickServ IDENTIFY nick password'])
    >>> bot.include('irc3.plugins.autocommand')

Here's another, more complicated example.

    >>> bot = IrcBot(autocommand=[
    ...     'AUTH user password', 'MODE {nick} +x', '/sleep 2',
    ...     'PRIVMSG Q INVITE #inviteonly'
    ... ])
    >>> bot.include('irc3.plugins.autocommand')

It will authorize bot in QuakeNet IRC network, cloak and then after 3 seconds
delay will request invite to ``#inviteonly`` channel.
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
        cmds = utils.as_list(self.bot.config.get('commands', []))
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
        asyncio.async(self.execute_commands(), loop=self.bot.loop)

    @asyncio.coroutine
    def execute_commands(self):
        for command in self.commands:
            yield from command.execute(self.bot)
