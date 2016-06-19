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
    ...     'PRIVMSG Q AUTH user password', 'MODE {nick} +x', '/sleep 2',
    ...     'PRIVMSG Q INVITE #inviteonly'
    ... ])
    >>> bot.include('irc3.plugins.autocommand')

It will authorize bot in QuakeNet IRC network, cloak and then after 3 seconds
delay will request invite to ``#inviteonly`` channel.
'''


@irc3.plugin
class AutoCommand:

    requires = [
        'irc3.plugins.core',
    ]

    SLEEP_RE = re.compile(r"^/sleep\s+(?P<time>[\d\.]+)\s*$", re.IGNORECASE)

    def __init__(self, bot):
        self.bot = bot
        self.commands = utils.as_list(self.bot.config.get('commands', []))

    def server_ready(self):
        # async deprecated since 3.4.4
        asyncio.async(self.execute_commands(), loop=self.bot.loop)

    @asyncio.coroutine
    def execute_commands(self):
        for command in self.commands:
            yield from self.process_command(command)

    @asyncio.coroutine
    def process_command(self, command):
        if not command:
            return

        if command.startswith('/'):
            sleep_m = self.SLEEP_RE.match(command)
            if sleep_m is not None:
                try:
                    val = float(sleep_m.groupdict()['time'])
                except ValueError:
                    self.bot.log.error("Wrong /sleep value")
                else:
                    yield from asyncio.sleep(val, loop=self.bot.loop)
        else:
            cmd = command.format(nick=self.bot.nick)
            self.bot.send_line(cmd)
