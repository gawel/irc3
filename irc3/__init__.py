# -*- coding: utf-8 -*-
from .dec import event
from .dec import plugin
from .utils import IrcString
from . import utils
from . import rfc
import venusian
import asyncio
import logging


class IrcConnection(asyncio.Protocol):  # pragma: no cover

    def connection_made(self, transport):
        self.transport = transport
        self.buf = ''

    def data_received(self, data):
        encoding = getattr(self, 'encoding', 'ascii')
        data = self.buf + data.decode(encoding, 'ignore')
        lines = data.split('\r\n')
        if data.endswith('\r\n'):
            self.buf = lines.pop(-1)
        else:
            self.buf = ''
        for line in data.split('\r\n'):
            self.factory.dispatch(line)

    def write(self, data):
        if data is not None:
            if isinstance(data, str):
                data = data.encode(self.encoding)
            if not data.endswith(b'\r\n'):
                data = data + b'\r\n'
            self.transport.write(data)

    def connection_lost(self, exc):
        self.factory.log.critical('connection lost: %r', exc)
        # reconnect
        self.factory.propagate('connection_lost')
        loop = asyncio.get_event_loop()
        t = asyncio.Task(
            loop.create_connection(
                self.__class__, self.factory.config.host,
                self.factory.config.port, ssl=self.factory.config.ssl))
        t.add_done_callback(self.connection_made)


class IrcBot:

    venusian = venusian
    event = event
    plugin = plugin
    rfc = rfc

    defaults = dict(
        nick='irc3',
        realname='irc3',
        info='Irc bot based on irc3',
        host='irc.freenode.net',
        port=6667,
        ssl=False,
        cmdchar='!',
        encoding='utf8',
        async=True,
    )

    def __init__(self, **config):
        self.config = utils.Config(dict(self.defaults, **config))
        self.async = self.config.async
        self.host = self.config['host']
        self.port = self.config['port']
        self.encoding = self.config['encoding']
        self.plugins = {}
        self.events = []
        self.log = logging.getLogger('irc3.' + self.nick)

    def get_plugin(self, ob):
        if isinstance(ob, str):
            plugins = [(p.__name__.lower(), p) for p in self.plugins.keys()]
            plugins = [(name, p) for name, p in plugins if name == ob]
            if len(plugins) == 1:
                return self.plugins[plugins[0][1]]
            else:
                names = [p.__name__.lower() for p in self.plugins.keys()]
                raise LookupError('Plugin %s not found in %s' % (ob, names))
        if ob not in self.plugins:
            self.log.info('Register plugin %r', ob.__name__.lower())
            plugin = ob(self)
            self.plugins[ob] = plugin
        return self.plugins[ob]

    def recompile(self):
        for e in self.events:
            e.compile(self.config)

    def add_event(self, event):
        self.events.append(event)

    def include(self, *modules):
        for module in modules:
            if isinstance(module, str):
                module = __import__(module, globals(), locals(), [''])
            scanner = self.venusian.Scanner(bot=self)
            scanner.scan(module)

    def connection_made(self, f):  # pragma: no cover
        self.log.info('Connected')
        transport, protocol = f.result()
        self.protocol = protocol
        self.protocol.factory = self
        self.protocol.encoding = self.encoding
        self.send((
            'USER %(nick)s %(realname)s %(host)s :%(info)s\r\n'
            'NICK %(nick)s\r\n') % self.config)
        self.propagate('connection_made')

    def propagate(self, event, exc=None):
        for p in self.plugins.values():
            meth = getattr(p, event, None)
            if meth is not None:
                meth()

    def dispatch(self, data):
        events = []
        for e in self.events:
            match = e.cregexp.search(data)
            if match is not None:
                match = match.groupdict()
                for key, value in match.items():
                    if value is not None:
                        match[key] = IrcString(value)
                if self.async:  # pragma: no cover
                    loop = asyncio.get_event_loop()
                    loop.call_soon(e.async_callback, match)
                else:
                    e.callback(**match)
                events.append((e, match))
        return events

    def send(self, data):  # pragma: no cover
        self.log.debug('> %s', data.strip())
        self.protocol.write(data)

    def privmsg(self, target, message):
        if message:
            self.send('PRIVMSG %s :%s\r\n' % (target, message))

    def join(self, target):
        self.send('JOIN %s\r\n' % target)

    def part(self, target, reason=None):
        if reason:
            target += ' :' + reason
        self.send('PART %s\r\n' % target)

    @property
    def nick(self):
        return self.config.nick

    def set_nick(self, nick):
        self.send('NICK ' + nick)

    def create_connection(self, loop=None,
                          protocol=IrcConnection):  # pragma: no cover
        if loop is None:
            loop = asyncio.get_event_loop()
        t = asyncio.Task(
            loop.create_connection(
                protocol, self.config.host,
                self.config.port, ssl=self.config.ssl))
        t.add_done_callback(self.connection_made)
        return loop
