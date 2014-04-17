# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__doc__ = '''
==============================================
:mod:`irc3.plugins.core` Core plugin
==============================================

Core events

.. autoclass:: Core
   :members:

..
    >>> from testing import IrcBot

Usage::

    >>> bot = IrcBot()
    >>> bot.include('irc3.plugins.core')
'''
from irc3 import utils
from irc3 import event
from irc3 import rfc


class Core(object):

    def __init__(self, bot):
        self.bot = bot
        self.timeout = int(self.bot.config.get('timeout'))
        self.ping_handle = None

    def connection_made(self):
        self.connection_made_at = self.bot.loop.time()
        if self.ping_handle is not None:
            self.ping_handle.cancel()
        self.ping_handle = self.bot.loop.call_later(self.timeout,
                                                    self.reconnect)

    def reconnect(self):  # pragma: no cover
        self.bot.log.info(
            "We're waiting a ping for too long. Trying to reconnect...")
        self.bot.loop.call_later(self.bot.protocol.transport.close)
        if self.ping_handle is not None:
            self.ping_handle.cancel()
        self.ping_handle = self.bot.loop.call_later(self.timeout,
                                                    self.reconnect)

    @event(rfc.PING)
    def pong(self, data):
        """PING reply"""
        if self.ping_handle is not None:
            self.ping_handle.cancel()
        self.ping_handle = self.bot.loop.call_later(self.timeout,
                                                    self.reconnect)
        self.bot.send('PONG ' + data)

    @event(rfc.NEW_NICK)
    def recompile(self, nick=None, new_nick=None, **kw):
        """recompile regexp on new nick"""
        if self.bot.nick == nick.nick:
            self.bot.config['nick'] = new_nick
            self.bot.recompile()

    @event(rfc.ERR_NICK)
    def badnick(self, me=None, nick=None, **kw):
        """Use alt nick on nick error"""
        if me == '*':
            self.bot.set_nick(self.bot.nick + '_')
        self.bot.log.debug('Trying to regain nickname in 30s...')
        self.bot.loop.call_later(30, self.bot.set_nick, self.bot.original_nick)

    @event(rfc.RPL_ENDOFMOTD)
    def autojoin(self, **kw):
        """autojoin at the end of MOTD"""
        self.bot.config['nick'] = kw['me']
        self.bot.recompile()
        channels = utils.as_list(self.bot.config.get('autojoins', []))
        for channel in channels:
            channel = utils.as_channel(channel)
            self.bot.log.info('Trying to join %s', channel)
            self.bot.join(channel)
