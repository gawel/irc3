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
class AutoJoins(object):

    requires = [
        'irc3.plugins.core',
    ]

    def __init__(self, bot):
        self.bot = bot
        self.channels = utils.as_list(self.bot.config.get('autojoins', []))
        self.handles = {}
        self.timeout = 240

    def connection_lost(self):  # pragma: no cover
        for timeout, handle in self.handles.values():
            handle.cancel()
        self.handles = {}

    def server_ready(self):
        self.join()

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
