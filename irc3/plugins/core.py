# -*- coding: utf-8 -*-
from irc3 import event
from irc3 import rfc
__doc__ = '''
==============================================
:mod:`irc3.plugins.core` Core plugin
==============================================

Core events

.. autoclass:: Core
   :members:

..
    >>> from irc3.testing import IrcBot

Usage::

    >>> bot = IrcBot()
    >>> bot.include('irc3.plugins.core')
'''


class Core:

    def __init__(self, bot):
        self.bot = bot
        self.timeout = int(self.bot.config.get('timeout'))
        self.max_lag = int(self.bot.config.get('max_lag'))
        self.reconn_handle = None
        self.ping_handle = None
        self.nick_handle = None
        self.before_connect_events = [
            event(rfc.CONNECTED, self.connected),
            event(r"^:\S+ 005 \S+ (?P<data>.+) :\S+.*",
                  self.set_config),
        ]

    def connection_made(self, client=None):
        # handle server config
        config = self.bot.defaults['server_config'].copy()
        self.bot.config['server_config'] = config
        self.bot.detach_events(*self.before_connect_events)
        self.bot.attach_events(insert=True, *self.before_connect_events)

        # ping/ping
        self.connection_made_at = self.bot.loop.time()
        self.pong(event='CONNECT', data='')

    def connected(self, **kwargs):
        """triger the server_ready event"""
        self.bot.log.info('Server config: %r', self.bot.server_config)

        # recompile when I'm sure of my nickname
        self.bot.config['nick'] = kwargs['me']
        self.bot.recompile()

        # Let all plugins know that server can handle commands
        self.bot.notify('server_ready')

        # detach useless events
        self.bot.detach_events(*self.before_connect_events)

    def reconnect(self):  # pragma: no cover
        self.bot.log.info(
            "We're waiting a ping for too long. Trying to reconnect...")
        self.bot.loop.call_soon(
            self.bot.protocol.connection_lost,
            'No pong reply'
        )
        self.pong(event='RECONNECT', data='')

    @event(rfc.PONG)
    def pong(self, event='PONG', data='', **kw):  # pragma: no cover
        """P0NG/PING"""
        self.bot.log.debug('%s ping-pong (%s)', event, data)
        if self.reconn_handle is not None:
            self.reconn_handle.cancel()
        self.reconn_handle = self.bot.loop.call_later(self.timeout,
                                                      self.reconnect)
        if self.ping_handle is not None:
            self.ping_handle.cancel()
        self.ping_handle = self.bot.loop.call_later(
            self.timeout - self.max_lag, self.bot.send,
            'PING :%s' % int(self.bot.loop.time()))

    @event(rfc.PING)
    def ping(self, data):
        """PING reply"""
        self.bot.send('PONG :' + data)
        self.pong(event='PING', data=data)

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
        self.nick_handle = self.bot.loop.call_later(
            30, self.bot.set_nick, self.bot.original_nick)

    def set_config(self, data=None, **kwargs):
        """Store server config"""
        config = self.bot.config['server_config']
        for opt in data.split(' '):
            if '=' in opt:
                opt, value = opt.split('=', 1)
            else:
                value = True
            if opt.isupper():
                config[opt] = value
