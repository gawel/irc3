# -*- coding: utf-8 -*-
__doc__ = '''
==============================================
:mod:`irc3.plugins.autojoins` Auto join plugin
==============================================

Auto join channels. The bot will retry to join when kicked and will retry to
join each 30s when an error occurs.

..
    >>> from testing import IrcBot

Usage::

    >>> bot = IrcBot(autojoins=['#chan1', '#chan2'])
    >>> bot.include('irc3.plugins.autojoins')
'''
import irc3
from irc3 import utils


@irc3.plugin
class AutoJoins(object):

    def __init__(self, bot):
        self.bot = bot
        self.channels = utils.as_list(self.bot.config.get('autojoins', []))

    def join(self, channel=None):
        if channel is None:
            channels = self.channels
        else:
            channels = [channel]
        for channel in channels:
            channel = utils.as_channel(channel)
            self.bot.log.info('Trying to join %s', channel)
            self.bot.join(channel)

    @irc3.event(irc3.rfc.RPL_ENDOFMOTD)
    def autojoin(self, **kw):
        """autojoin at the end of MOTD"""
        self.bot.config['nick'] = kw['me']
        self.bot.recompile()
        self.join()

    @irc3.event(irc3.rfc.KICK)
    def on_kick(self, mask, channel, target, **kwargs):
        """bot must rejoin when kicked from a channel"""
        if target.nick == self.bot.nick:
            self.join(channel)

    @irc3.event("^:\S+ 47[12345] \S+ (?P<channel>\S+).*")
    def on_err_join(self, channel, **kwargs):
        """bot must try to rejoin later when he can't join"""
        self.bot.loop.call_later(30, self.join, channel)
