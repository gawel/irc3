# -*- coding: utf-8 -*-
from urllib.request import urlopen
from ipaddress import ip_address
from collections import deque
from .dcc import DCCManager
from .dcc import DCCChat
from .dec import dcc_event
from .dec import event
from .dec import extend
from .dec import plugin
from . import config
from . import utils
from . import rfc
from . import base
from .compat import asyncio
from .compat import Queue
import venusian
import time


class IrcConnection(asyncio.Protocol):
    """asyncio protocol to handle an irc connection"""

    def connection_made(self, transport):
        self.transport = transport
        self.closed = False
        self.queue = deque()

    def decode(self, data):
        """Decode data with bot's encoding"""
        encoding = getattr(self, 'encoding', 'ascii')
        return data.decode(encoding, 'ignore')

    def data_received(self, data):
        data = self.decode(data)
        if self.queue:
            data = self.queue.popleft() + data
        lines = data.split('\r\n')
        self.queue.append(lines.pop(-1))
        for line in lines:
            self.factory.dispatch(line)

    def write(self, data):
        if data is not None:
            data = data.encode(self.encoding)
            if not data.endswith(b'\r\n'):
                data = data + b'\r\n'
            self.transport.write(data)

    def connection_lost(self, exc):
        self.factory.log.critical('connection lost (%s): %r',
                                  id(self.transport),
                                  exc)
        self.factory.notify('connection_lost')
        if not self.closed:
            self.close()
            # wait a few before reconnect
            self.factory.loop.call_later(
                2, self.factory.create_connection)

    def close(self):
        if not self.closed:
            self.factory.log.critical('closing old transport (%r)',
                                      id(self.transport))
            try:
                self.transport.close()
            finally:
                self.closed = True


class IrcBot(base.IrcObject):
    """An IRC bot"""

    _pep8 = [dcc_event, event, extend, plugin, rfc, config]
    venusian = venusian
    venusian_categories = [
        'irc3',
        'irc3.dcc',
        'irc3.extend',
        'irc3.rfc1459',
        'irc3.plugins.cron',
        'irc3.plugins.command',
    ]

    logging_config = config.LOGGING

    defaults = dict(
        base.IrcObject.defaults,
        nick='irc3',
        username='irc3',
        realname='Irc bot based on irc3 http://irc3.readthedocs.io',
        host='localhost',
        mode=0,
        url='https://irc3.readthedocs.io/',
        passwords={},
        flood_burst=4,
        flood_rate=1,
        flood_rate_delay=1,
        ctcp=dict(
            version='irc3 {version} - {url}',
            userinfo='{realname}',
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
        update_config_needed = False
        if 'userinfo' in config or \
           ('realname' in config and 'username' not in config):
            update_config_needed = True  # pragma: no cover
        super(IrcBot, self).__init__(*ini, **config)
        if update_config_needed:  # pragma: no cover
            # Backward compat. Remove me in 2017
            self.log.fatal('realname has been renamed to username.')
            self.log.fatal('userinfo has been renamed to realname.')
            self.log.fatal('Please update your config with something like:.')
            if 'realname' in self.config:
                self.log.fatal('username = %(realname)s', self.config)
            if 'userinfo' in self.config:
                self.log.fatal('realname = %(userinfo)s', self.config)
            import sys
            sys.exit(-1)
        self.queue = None
        if self.config.async:
            self.queue = Queue(loop=self.loop)
            self.awaiting_queue = self.create_task(self.process_queue())
        self._ip = self._dcc = None
        # auto include the sasl plugin if needed
        if 'sasl_username' in self.config and \
           'irc3.plugins.sasl' not in self.registry.includes:
            self.include('irc3.plugins.sasl')
        # auto include the autojoins plugin if needed (for backward compat)
        if 'autojoins' in self.config and \
           'irc3.plugins.autojoins' not in self.registry.includes:
            self.include('irc3.plugins.autojoins')

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
            self.protocol.queue = deque()
            self.protocol.factory = self
            self.protocol.encoding = self.encoding
            if self.config.get('password'):
                self._send('PASS {password}'.format(**self.config))
            self.notify('connection_ready')
            self.send((
                'USER {username} {mode} * :{realname}\r\n'
                'NICK {nick}\r\n'
            ).format(**self.config))
            self.notify('connection_made')

    def send_line(self, data, nowait=False):
        """send a line to the server. replace CR by spaces"""
        data = data.replace('\n', ' ').replace('\r', ' ')
        f = asyncio.Future(loop=self.loop)
        if self.queue is not None and nowait is False:
            self.queue.put_nowait((f, data))
        else:
            self.send(data.replace('\n', ' ').replace('\r', ' '))
            f.set_result(True)
        return f

    @asyncio.coroutine
    def process_queue(self):
        flood_burst = self.config.flood_burst
        delay = float(self.config.flood_rate_delay)
        flood_rate = delay / float(self.config.flood_rate)
        while True:
            if flood_burst == 0:
                future, data = yield from self.queue.get()
                future.set_result(True)
                self.send(data)
                yield from asyncio.sleep(.001, loop=self.loop)
            else:
                lines = []
                for i in range(flood_burst):
                    future, data = yield from self.queue.get()
                    future.set_result(True)
                    lines.append(data)
                    if self.queue.empty():
                        break
                if lines:
                    self.send(u'\r\n'.join(lines))
                while not self.queue.empty():
                    yield from asyncio.sleep(flood_rate, loop=self.loop)
                    future, data = yield from self.queue.get()
                    future.set_result(True)
                    self.send(data)

    def send(self, data):
        """send data to the server"""
        self._send(data)

    def _send(self, data):
        self.protocol.write(data)
        self.dispatch(data, iotype='out')

    def privmsg(self, target, message, nowait=False):
        """send a privmsg to target"""
        if message:
            messages = utils.split_message(message, self.config.max_length)
            if isinstance(target, DCCChat):
                for message in messages:
                    target.send_line(message)
            elif target:
                f = None
                for message in messages:
                    f = self.send_line('PRIVMSG %s :%s' % (target, message),
                                       nowait=nowait)
                return f

    def notice(self, target, message, nowait=False):
        """send a notice to target"""
        if message:
            messages = utils.split_message(message, self.config.max_length)
            if isinstance(target, DCCChat):
                for message in messages:
                    target.action(message)
            elif target:
                f = None
                for message in messages:
                    f = self.send_line('NOTICE %s :%s' % (target, message),
                                       nowait=nowait)
                return f

    def ctcp(self, target, message, nowait=False):
        """send a ctcp to target"""
        if target and message:
            messages = utils.split_message(message, self.config.max_length)
            f = None
            for message in messages:
                f = self.send_line('PRIVMSG %s :\x01%s\x01' % (target,
                                                               message),
                                   nowait=nowait)
            return f

    def ctcp_reply(self, target, message, nowait=False):
        """send a ctcp reply to target"""
        if target and message:
            messages = utils.split_message(message, self.config.max_length)
            f = None
            for message in messages:
                f = self.send_line('NOTICE %s :\x01%s\x01' % (target, message),
                                   nowait=nowait)
            return f

    def mode(self, target, *data):
        """set user or channel mode"""
        self.send_line('MODE %s %s' % (target, ' '.join(data)), nowait=True)

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
        self.send_line('KICK %s %s' % (channel, target), nowait=True)

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
        self.send_line('NICK ' + nick, nowait=True)

    nick = property(get_nick, set_nick, doc='nickname get/set')

    @property
    def ip(self):
        """return bot's ip as an ``ip_address`` object"""
        if not self._ip:
            if 'ip' in self.config:
                ip = self.config['ip']
            else:
                ip = self.protocol.transport.get_extra_info('sockname')[0]
            ip = ip_address(ip)
            if ip.version == 4:
                self._ip = ip
            else:  # pragma: no cover
                response = urlopen('http://ipv4.icanhazip.com/')
                ip = response.read().strip().decode()
                ip = ip_address(ip)
                self._ip = ip
        return self._ip

    @property
    def dcc(self):
        """return the :class:`~irc3.dcc.DCCManager`"""
        if self._dcc is None:
            self._dcc = DCCManager(self)
        return self._dcc

    @asyncio.coroutine
    def dcc_chat(self, mask, host=None, port=None):
        """Open a DCC CHAT whith mask. If host/port are specified then connect
        to a server. Else create a server"""
        return self.dcc.create(
            'chat', mask, host=host, port=port).ready

    @asyncio.coroutine
    def dcc_get(self, mask, host, port, filepath, filesize=None):
        """DCC GET a file from mask. filepath must be an absolute path with an
        existing directory. filesize is the expected file size."""
        return self.dcc.create(
            'get', mask, filepath=filepath, filesize=filesize,
            host=host, port=port).ready

    @asyncio.coroutine
    def dcc_send(self, mask, filepath):
        """DCC SEND a file to mask. filepath must be an absolute path to
        existing file"""
        return self.dcc.create('send', mask, filepath=filepath).ready

    @asyncio.coroutine
    def dcc_accept(self, mask, filepath, port, pos):
        """accept a DCC RESUME for an axisting DCC SEND. filepath is the
        filename to sent.  port is the port opened on the server.
        pos is the expected offset"""
        return self.dcc.resume(mask, filepath, port, pos)

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
