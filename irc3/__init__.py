# -*- coding: utf-8 -*-
from collections import defaultdict
from .dec import event
from .dec import extend
from .dec import plugin
from .utils import IrcString
from . import config
from . import utils
from . import rfc
import logging.config
import logging
import venusian
import asyncio
import signal
import time


class IrcConnection(asyncio.Protocol):  # pragma: no cover

    def connection_made(self, transport):
        self.transport = transport
        self.closed = False
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
        self.factory.log.critical('connection lost (%s): %r',
                                  id(self.transport),
                                  exc)
        self.factory.notify('connection_lost')
        if not self.closed:
            self.close()
            # wait a few before reconnect
            time.sleep(2)
            # reconnect
            self.factory.create_connection(protocol=self.__class__)

    def close(self):
        if not self.closed:
            self.factory.log.critical('closing old transport (%r)',
                                      id(self.transport))
            try:
                self.transport.close()
            finally:
                self.closed = True


class IrcBot:

    _pep8 = [event, extend, plugin, rfc, config]
    venusian = venusian
    venusian_categories = [
        'irc3.plugin',
        'irc3.extend',
        'irc3.rfc1459',
        'irc3.plugins.command',
    ]

    logging_config = config.LOGGING

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
        loop=None,
    )

    def __init__(self, **config):
        self.config = utils.Config(dict(self.defaults, **config))
        logging.config.dictConfig(self.logging_config)
        self.log = logging.getLogger('irc3.' + self.nick)
        if config.get('verbose'):
            logging.getLogger('irc3').setLevel(logging.DEBUG)
        self.encoding = self.config['encoding']
        self.loop = self.config.loop
        self.events_re = []
        self.events = defaultdict(list)
        self._sent = []

        self.plugins = {}
        self.includes = set()
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
        events_re = []
        for regexp, cregexp in self.events_re:
            e = self.events[regexp][0]
            e.compile(self.config)
            events_re.append((regexp, e.cregexp))
        self.events_re = events_re

    def add_event(self, event):
        if event.regexp not in self.events_re:
            self.events_re.append((event.regexp, event.cregexp))
        self.events[event.regexp].append(event)

    def include(self, *modules, **kwargs):
        categories = kwargs.get('venusian_categories',
                                self.venusian_categories)
        for module in modules:
            if module in self.includes:
                self.log.warn('%s included twice', module)
            self.includes.add(module)
            scanner = self.venusian.Scanner(bot=self)
            scanner.scan(utils.maybedotted(module), categories=categories)

    def connection_made(self, f):  # pragma: no cover
        if getattr(self, 'protocol', None):
            self.protocol.close()
        self.log.info('Connected')
        transport, protocol = f.result()
        self.protocol = protocol
        self.protocol.factory = self
        self.protocol.encoding = self.encoding
        self.send((
            'USER %(nick)s %(realname)s %(host)s :%(info)s\r\n'
            'NICK %(nick)s\r\n') % self.config)
        self.notify('connection_made')

    def notify(self, event, exc=None):
        for p in self.plugins.values():
            meth = getattr(p, event, None)
            if meth is not None:
                meth()

    def dispatch(self, data):
        events = []
        for regexp, cregexp in self.events_re:
            match = cregexp.search(data)
            if match is not None:
                match = match.groupdict()
                for key, value in match.items():
                    if value is not None:
                        match[key] = IrcString(value)
                for e in self.events[regexp]:
                    if self.config.async:  # pragma: no cover
                        self.loop.call_soon(e.async_callback, match)
                    else:
                        e.callback(**match)
                    events.append((e, match))
        return events

    def send(self, data):
        """send data to the server"""
        if not self.config.testing:  # pragma: no cover
            self.log.debug('> %s', data.strip())
            self.protocol.write(data)
        else:
            self._sent.append(data)

    def call_many(self, callback, args):
        """callback is run with each arg but run a call per second"""
        if isinstance(callback, str):
            callback = getattr(self, callback)
        for i, arg in enumerate(args):
            if self.loop:  # pragma: no cover
                self.loop.call_later(i, callback, *arg)
            else:
                callback(*arg)

    def privmsg(self, target, message):
        """send a privmsg to target"""
        if target and message:
            self.send('PRIVMSG %s :%s' % (target, message))

    def notice(self, target, message):
        """send a notice to target"""
        if target and message:
            self.send('NOTICE %s :%s' % (target, message))

    def join(self, target):
        """join a channel"""
        self.send('JOIN %s' % target)

    def part(self, target, reason=None):
        """quit a channel"""
        if reason:
            target += ' :' + reason
        self.send('PART %s' % target)

    def quit(self, reason=None):
        """disconnect"""
        if not reason:
            reason = 'bye'
        self.send('QUIT :%s' % reason)

    def get_nick(self):
        """nickname"""
        return self.config.nick

    def set_nick(self, nick):
        self.send('NICK ' + nick)

    nick = property(get_nick, set_nick)

    def test(self, data):
        self.dispatch(data)

    @property
    def sent(self):
        sent = self._sent
        self._sent = []
        return sent

    def create_connection(self, protocol=IrcConnection):  # pragma: no cover
        if self.loop is None:
            self.loop = asyncio.get_event_loop()
        t = asyncio.Task(
            self.loop.create_connection(
                protocol, self.config.host,
                self.config.port, ssl=self.config.ssl),
            loop=self.loop)
        t.add_done_callback(self.connection_made)
        return self.loop

    def SIGHUP(self):  # pragma: no cover
        self.quit('HUP')
        time.sleep(1)
        try:
            self.protocol.transport.close()
        finally:
            pass

    def SIGINT(self):  # pragma: no cover
        if self.protocol:
            self.quit('INT')
            time.sleep(1)
        self.loop.stop()

    def run(self):  # pragma: no cover
        """start the bot"""
        loop = self.create_connection()
        loop.add_signal_handler(signal.SIGHUP, self.SIGHUP)
        loop.add_signal_handler(signal.SIGINT, self.SIGINT)
        loop.run_forever()


def run(argv=None):
    """
    Run an irc bot from a config file

    Usage: irc3 [options] <config>

    Options:

    --logdir DIRECTORY  Log directory to use instead of stderr
    -v,--verbose        Increase verbosity
    -r,--raw            Show raw irc log on the console
    -d,--debug          Add some debug commands/utils
    """
    import os
    import sys
    import docopt
    import textwrap
    args = argv or sys.argv[1:]
    args = docopt.docopt(textwrap.dedent(run.__doc__), args)
    cfg = utils.parse_config(args['<config>'])
    cfg.update(
        verbose=args['--verbose'],
    )
    if args['--logdir'] or 'logdir' in cfg:
        logdir = os.path.expanduser(args['--logdir'] or cfg.get('logdir'))
        IrcBot.logging_config = config.get_file_config(logdir)
    if args['--debug']:
        IrcBot.venusian_categories.append('irc3.debug')
    bot = IrcBot(**cfg)
    if args['--raw']:
        bot.include('irc3.plugins.log', venusian_categories=['irc3.debug'])
    if argv:
        return bot
    bot.run()  # pragma: no cover
