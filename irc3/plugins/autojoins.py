# -*- coding: utf-8 -*-
import irc3
from irc3 import utils
__doc__ = '''
==============================================
:mod:`irc3.plugins.autojoins` Auto join plugin
==============================================

Auto join channels. The bot will retry to join when kicked and will retry to
join each 30s when an error occurs.

..
    >>> from irc3.testing import IrcBot

Usage::

    >>> bot = IrcBot(autojoins=['#chan1', '#chan2'])
    >>> bot.include('irc3.plugins.autojoins')
'''


@irc3.plugin
class AutoJoins:

    requires = [
        'irc3.plugins.core',
    ]

    def __init__(self, bot):
        self.bot = bot
        self.channels = utils.as_list(self.bot.config.get('autojoins', []))
        self.delay = self.bot.config.get('autojoin_delay', 0)
        self.handles = {}
        self.timeout = 240
        self.joined = set()
        self.delayed_join = None
        if not isinstance(self.delay, (int, float)):  # pragma: no cover
            self.bot.log.error('Wrong autojoin_delay value: %r', self.delay)
            self.delay = 0

    @classmethod
    def reload(cls, old):
        if hasattr(old, "joined"):
            old_channels = old.joined
        else:  # pragma: no cover
            # old version of plugin
            old_channels = frozenset(old.channels)

        new = cls(old.bot)
        new_channels = frozenset(new.channels)
        part_channels = old_channels - new_channels
        join_channels = new_channels - old_channels
        # join to new channels
        for channel in join_channels:
            new.join(channel)

        # part from old channels
        for channel in part_channels:
            new.part(channel)
        return new

    def before_reload(self):  # pragma: no cover
        self.stop_tasks()

    def stop_tasks(self):  # pragma: no cover
        if self.delayed_join is not None:
            self.delayed_join.cancel()
            self.delayed_join = None

        for timeout, handle in self.handles.values():
            handle.cancel()
        self.handles = {}

    def connection_lost(self):  # pragma: no cover
        self.stop_tasks()

    def server_ready(self):
        if not self.delay:
            self.join()
        else:
            task = self.bot.loop.call_later(self.delay, self.join)
            self.delayed_join = task

    def join(self, channel=None):
        if channel is None:
            channels = self.channels
        else:
            channels = [channel]
        for channel in channels:
            channel = utils.as_channel(channel)
            if channel in self.handles:
                timeout, handle = self.handles[channel]
                self.bot.log.info('Re-trying to join %s after %ss',
                                  channel, timeout)
            else:
                self.bot.log.info('Trying to join %s', channel)
            self.bot.join(channel)
            self.joined.add(channel)

    def part(self, channel):
        channel = utils.as_channel(channel)
        self.bot.log.info('Leaving channel %s', channel)
        self.bot.part(channel)
        if channel in self.joined:  # pragma: no cover
            self.joined.remove(channel)

    @irc3.event(irc3.rfc.KICK)
    def on_kick(self, mask, channel, target, **kwargs):
        """bot must rejoin when kicked from a channel"""
        if channel in self.handles:
            timeout, handle = self.handles[channel]
            handle.cancel()
            del self.handles[channel]
        if target.nick == self.bot.nick:
            self.join(channel)

    @irc3.event("^:\S+ 47[1234567] \S+ (?P<channel>\S+).*")
    def on_err_join(self, channel, **kwargs):
        """bot must try to rejoin later when he can't join"""
        if channel in self.handles:
            timeout, handle = self.handles[channel]
            handle.cancel()
            timeout = timeout * 4
            if timeout > self.timeout:  # pragma: no cover
                timeout = self.timeout
        else:
            timeout = 2
        handle = self.bot.loop.call_later(timeout, self.join, channel)
        self.handles[channel] = timeout, handle
        if channel in self.joined:
            self.joined.remove(channel)
