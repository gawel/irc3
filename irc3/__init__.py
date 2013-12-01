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
        testing=False,
        async=True,
    )

    def __init__(self, **config):
        self.config = utils.Config(dict(self.defaults, **config))
        self.async = self.config.async
        self.encoding = self.config['encoding']
        self.events = []
        self.log = logging.getLogger('irc3.' + self.nick)
        self._sent = []

        self.plugins = {}
        self.include(*self.config.get('includes', []))
        self.recompile()

    def get_plugin(self, ob):
        if isinstance(ob, str):
            name = ob
            ob = utils.maybedotted(ob)
            if ob not in self.plugins:
                plugins = [(p.__module__, p.__name__)
                           for p in self.plugins.keys()]
                names = ['%s.%s' % p for p in plugins]
                raise LookupError('Plugin %s not found in %s' % (name, names))
        if ob not in self.plugins:
            self.log.info("Register plugin '%s.%s'",
                          ob.__module__, ob.__name__)
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
            scanner = self.venusian.Scanner(bot=self)
            scanner.scan(utils.maybedotted(module))

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

    def send(self, data):
        if not self.config.testing:  # pragma: no cover
            self.log.debug('> %s', data.strip())
            self.protocol.write(data)
        else:
            self._sent.append(data)

    def privmsg(self, target, message):
        if message:
            self.send('PRIVMSG %s :%s' % (target, message))

    def join(self, target):
        self.send('JOIN %s' % target)

    def part(self, target, reason=None):
        if reason:
            target += ' :' + reason
        self.send('PART %s\r\n' % target)

    @property
    def nick(self):
        return self.config.nick

    def set_nick(self, nick):
        self.send('NICK ' + nick)

    def test(self, data):
        self.dispatch(data)

    @property
    def sent(self):
        sent = self._sent
        self._sent = []
        return sent

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
