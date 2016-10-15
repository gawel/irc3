# -*- coding: utf-8 -*-
from irc3.plugins.command import command
import time
import irc3
__doc__ = '''
==============================================
:mod:`irc3.plugins.uptime` Uptime plugin
==============================================

Add an ``uptime`` command.

.. autoclass:: Uptime
   :members:

'''


@irc3.plugin
class Uptime:

    requires = [
        __name__.replace('uptime', 'command'),
    ]

    def __init__(self, bot):
        self.bot = bot
        bot.uptime = self
        self.uptime = time.time()
        self.connection_uptime = None
        config = bot.config.get(__name__, {})
        self.fmt = config.get(
            'fmt', '{days} days {hours} hours {minutes} minutes')
        self.privmsg = config.get('privmsg',
                                  'Up since {0}. Connected since {1}')

    def connection_made(self):
        self.connection_uptime = time.time()

    def delta(self, value):
        values = []
        for base in [3600*24, 3600, 60, 1]:
            d, value = divmod(value, base)
            values.append(int(d))
        values = dict(zip(['days', 'hours', 'minutes', 'seconds'], values))
        return self.fmt.format(**values)

    @command(permission='view')
    def uptime(self, mask, target, args):
        """Show uptimes

            %%uptime
        """
        now = time.time()
        uptime = self.delta(now - self.uptime)
        connection_uptime = self.delta(now - (self.connection_uptime or now))
        return self.privmsg.format(uptime, connection_uptime)
