# -*- coding: utf-8 -*-
import time
import venusian
from os import path
from irc3 import base
from irc3 import utils
from irc3 import config
from irc3.compat import asyncio
from irc3.compat import Queue
from collections import defaultdict
from .plugins.command import command
from .dec import plugin
from .dec import extend
from .dec import event


class IrcClient(asyncio.Protocol):
    """asyncio protocol to handle an irc connection"""

    def connection_made(self, transport):
        self.closed = False
        self.transport = transport
        self.queue = Queue()
        self.uuid = self.transport.get_extra_info('peername')
        self.factory.clients[self.uuid] = self
        self.encoding = self.factory.encoding
        self.data = {}
        self.modes = set()
        self.channels = set()
        t = time.time()
        self.data.update(
            uuid=self.uuid, host=self.uuid[0],
            connection_made=t, data_received=t,
            srv=self.factory.config.servername,
            version=self.factory.config.version)

    def __getattr__(self, attr):
        return self.data[attr]

    def get_nick(self):
        return self.data.get('nick')

    def set_nick(self, nick):
        self.data['nick'] = nick
        self.data['mask'] = utils.IrcString(
            '{nick}!{username}@{uuid[0]}'.format(**self.data))

    nick = property(get_nick, set_nick)

    @property
    def registered(self):
        return bool('nick' in self.data and 'username' in self.data)

    def decode(self, data):  # pragma: no cover
        """Decode data with bot's encoding"""
        encoding = getattr(self, 'encoding', 'ascii')
        return data.decode(encoding, 'ignore')

    def data_received(self, data):  # pragma: no cover
        self.data['data_received'] = time.time()
        data = self.decode(data)
        if not self.queue.empty():
            data = self.queue.get_nowait() + data
        lines = data.split('\r\n')
        self.queue.put_nowait(lines.pop(-1))
        for line in lines:
            self.factory.dispatch(line, client=self)

    def fwrite(self, messages, **kwargs):
        kwargs['c'] = self
        if not isinstance(messages, (list, tuple)):
            fmt = getattr(messages, 'tpl', messages)
        else:
            fmt = '\r\n'.join([getattr(m, 'tpl', m) for m in messages])
        self.write(fmt.format(**kwargs))

    def write(self, data):
        if data is not None:
            self.factory.dispatch(data, client=self, iotype='out')
            data = data.encode(self.encoding)
            if not data.endswith(b'\r\n'):
                data = data + b'\r\n'
            self.transport.write(data)

    def connection_lost(self, exc):
        self.factory.log.critical('connection lost (%s): %r',
                                  id(self.transport),
                                  exc)
        self.factory.notify('connection_lost', client=self)
        del self.factory.clients[self.uuid]
        if not self.closed:
            self.closed = True
            self.close()

    def close(self):  # pragma: no cover
        if not self.closed:
            self.factory.log.critical('closing old transport (%r)',
                                      id(self.transport))
            try:
                self.transport.close()
            finally:
                self.closed = True

    def __str__(self):
        if 'nick' in self.data:
            return '{nick}'.format(**self.data)
        else:
            return 'unknown'

    __repr__ = __str__


class IrcServer(base.IrcObject):
    """An irc server"""

    nick = None
    server = True
    plugin_category = '__irc3_plugin__'

    _pep8 = [config, extend, plugin, event, command]
    venusian = venusian
    venusian_categories = [
        'irc3d',
        'irc3d.extend',
        'irc3d.rfc1459',
        'irc3d.plugins.command',
    ]

    server_config = {
        'NETWORK': 'freenode', 'MODES': '1', 'DEAF': 'D', 'SAFELIST': True,
        'CHANTYPES': '#', 'TARGMAX':
        'NAMES:1,LIST:1,KICK:1,WHOIS:1,PRIVMSG:1,NOTICE:1,ACCEPT:,MONITOR:',
        'CNOTICE': True, 'TOPICLEN': '390', 'EXTBAN': '$,ajrxz',
        'CALLERID': 'g', 'ETRACE': True, 'CHANLIMIT': '#:120', 'CHARSET':
        'ascii', 'PREFIX': '(ov)@+', 'INVEX': True, 'NICKLEN': '16',
        'CLIENTVER': '3.0', 'CPRIVMSG': True, 'CHANMODES':
        '', 'MAXLIST': 'bqeI:100', 'KNOCK':
        True, 'EXCEPTS': True, 'CHANNELLEN': '50', 'CASEMAPPING':
        'rfc1459', 'FNC': True, 'STATUSMSG': '@+', 'ELIST': 'CTU', 'WHOX':
        True, 'MONITOR': '100'}

    defaults = dict(
        base.IrcObject.defaults,
        motd=path.join(path.dirname(__file__), 'motd.txt'),
        cmd='',
        host='0.0.0.0',
        port=6667,
        connection=IrcClient,
        server_config=server_config,
        servername='localhost',
    )

    def __init__(self, *args, **kwargs):
        self.clients = defaultdict(dict)
        super(IrcServer, self).__init__(*args, **kwargs)

    def connection_made(self, f):  # pragma: no cover
        if getattr(self, 'protocol', None):
            self.protocol.close()
        try:
            f.result()
        except Exception as e:
            self.log.exception(e)
            self.loop.call_later(3, self.create_connection)
        else:
            self.log.info('Started')

    def notice(self, client, message):
        """send a notice to client"""
        if client and message:
            messages = utils.split_message(message, self.config.max_length)
            for msg in messages:
                client.fwrite(':{c.srv} NOTICE {c.nick} :{msg}', msg=msg)

    privmsg = notice

    def SIGHUP(self, *args):  # pragma: no cover
        self.loop.stop()

    def SIGINT(self, *args):  # pragma: no cover
        self.loop.stop()


def run(argv=None):
    return IrcServer.from_argv(argv)
