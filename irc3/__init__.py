# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .dec import event
from .dec import extend
from .dec import plugin
from . import config
from . import utils
from . import rfc
from . import base
from .compat import text_type
from .compat import asyncio
from .compat import Queue
import venusian
import time


class IrcConnection(asyncio.Protocol):
    """asyncio protocol to handle an irc connection"""

    def connection_made(self, transport):
        self.transport = transport
        self.closed = False
        self.queue = Queue()

    def decode(self, data):
        """Decode data with bot's encoding"""
        encoding = getattr(self, 'encoding', 'ascii')
        return data.decode(encoding, 'ignore')

    def data_received(self, data):
        data = self.decode(data)
        if not self.queue.empty():
            data = self.queue.get_nowait() + data
        lines = data.split('\r\n')
        self.queue.put_nowait(lines.pop(-1))
        for line in lines:
            self.factory.dispatch(line)

    def encode(self, data):
        """Encode data with bot's encoding"""
        if isinstance(data, text_type):
            data = data.encode(self.encoding)
        return data

    def write(self, data):
        if data is not None:
            data = self.encode(data)
            if not data.endswith(b'\r\n'):
                data = data + b'\r\n'
            self.transport.write(data)

    def connection_lost(self, exc):  # pragma: no cover
        self.factory.log.critical('connection lost (%s): %r',
                                  id(self.transport),
                                  exc)
        self.factory.notify('connection_lost')
        if not self.closed:
            self.closed = True
            self.close()
            # wait a few before reconnect
            self.factory.loop.call_later(
                2, self.factory.create_connection)

    def close(self):  # pragma: no cover
        if not self.closed:
            self.factory.log.critical('closing old transport (%r)',
                                      id(self.transport))
            try:
                self.transport.close()
            finally:
                self.closed = True


class IrcBot(base.IrcObject):
    """An IRC bot"""

    _pep8 = [event, extend, plugin, rfc, config]
    venusian = venusian
    venusian_categories = [
        'irc3',
        'irc3.extend',
        'irc3.rfc1459',
        'irc3.plugins.cron',
        'irc3.plugins.command',
    ]

    logging_config = config.LOGGING

    defaults = dict(
        base.IrcObject.defaults,
        nick='irc3',
        realname='irc3',
        userinfo='Irc bot based on irc3 http://irc3.readthedocs.org',
        host='localhost',
        url='https://irc3.readthedocs.org/',
        passwords={},
        ctcp=dict(
            version='irc3 {version} - {url}',
            userinfo='{userinfo}',
            time='{now:%c}',
        ),
        # freenode config as default for testing
        server_config=dict(
            STATUSMSG='+@',
            PREFIX='(ov)@+',
            CHANTYPES='#',
            CHANMODES='eIbq,k,flj,CFLMPQScgimnprstz',
        ),
        connection=IrcConnection,
    )

    def __init__(self, *ini, **config):
        super(IrcBot, self).__init__(*ini, **config)
        # auto include the autojoins plugin if needed (for backward compat)
        if 'autojoins' in self.config and \
           'irc3.plugins.autojoins' not in self.includes:
            self.include('irc3.plugins.autojoins')
        self.recompile()

    @property
    def server_config(self):
        """return server configuration (rfc rpl 005)::

            >>> bot = IrcBot()
            >>> print(bot.server_config['STATUSMSG'])
            +@

        The real values are only available after the server sent them.
        """
        return self.config.server_config

    def connection_made(self, f):  # pragma: no cover
        if getattr(self, 'protocol', None):
            self.protocol.close()
        try:
            transport, protocol = f.result()
        except Exception as e:
            self.log.exception(e)
            self.loop.call_later(3, self.create_connection)
        else:
            self.log.debug('Connected')
            self.protocol = protocol
            self.protocol.queue = Queue(loop=self.loop)
            self.protocol.factory = self
            self.protocol.encoding = self.encoding
            if self.config.get('password'):
                self._send('PASS {password}'.format(**self.config))
            self.send((
                'USER {realname} {host} {host} :{userinfo}\r\n'
                'NICK {nick}\r\n'
            ).format(**self.config))
            self.notify('connection_made')

    def send_line(self, data):
        """send a line to the server. replace CR by spaces"""
        self.send(data.replace('\n', ' ').replace('\r', ' '))

    def send(self, data):
        """send data to the server"""
        self._send(data)

    def _send(self, data):
        self.protocol.write(data)
        self.dispatch(data, iotype='out')

    def privmsg(self, target, message):
        """send a privmsg to target"""
        if target and message:
            messages = utils.split_message(message, self.config.max_length)
            for message in messages:
                self.send_line('PRIVMSG %s :%s' % (target, message))

    def notice(self, target, message):
        """send a notice to target"""
        if target and message:
            messages = utils.split_message(message, self.config.max_length)
            for message in messages:
                self.send_line('NOTICE %s :%s' % (target, message))

    def ctcp(self, target, message):
        """send a ctcp to target"""
        if target and message:
            messages = utils.split_message(message, self.config.max_length)
            for message in messages:
                self.send_line('PRIVMSG %s :\x01%s\x01' % (target, message))

    def ctcp_reply(self, target, message):
        """send a ctcp reply to target"""
        if target and message:
            messages = utils.split_message(message, self.config.max_length)
            for message in messages:
                self.send_line('NOTICE %s :\x01%s\x01' % (target, message))

    def mode(self, target, *data):
        """set user or channel mode"""
        self.send_line('MODE %s %s' % (target, ' '.join(data)))

    def join(self, target):
        """join a channel"""
        password = self.config.passwords.get(
            target.strip(self.server_config['CHANTYPES']))
        if password:
            target += ' ' + password
        self.send_line('JOIN %s' % target)

    def part(self, target, reason=None):
        """quit a channel"""
        if reason:
            target += ' :' + reason
        self.send_line('PART %s' % target)

    def kick(self, channel, target, reason=None):
        """kick target from channel"""
        if reason:
            target += ' :' + reason
        self.send_line('KICK %s %s' % (channel, target))

    def invite(self, target, channel):
        """invite target to a channel"""
        self.send_line('INVITE %s %s' % (target, channel))

    def topic(self, channel, topic=None):
        """change or request the topic of a channel"""
        if topic:
            channel += ' :' + topic
        self.send_line('TOPIC %s' % channel)

    def away(self, message=None):
        """mark ourself as away"""
        cmd = 'AWAY'
        if message:
            cmd += ' :' + message
        self.send_line(cmd)

    def unaway(self):
        """mask ourself as no longer away"""
        self.away()

    def quit(self, reason=None):
        """disconnect"""
        if not reason:
            reason = 'bye'
        else:
            reason = reason
        self.send_line('QUIT :%s' % reason)

    def get_nick(self):
        return self.config.nick

    def set_nick(self, nick):
        self.send_line('NICK ' + nick)

    nick = property(get_nick, set_nick, doc='nickname get/set')

    def SIGHUP(self):
        self.reload()

    def SIGINT(self):
        self.notify('SIGINT')
        if getattr(self, 'protocol', None):
            self.quit('INT')
            time.sleep(1)
        self.loop.stop()


def run(argv=None):
    return IrcBot.from_argv(argv)
