# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import defaultdict
from .dec import event
from .dec import extend
from .dec import plugin
from .utils import IrcString
from . import config
from . import utils
from . import rfc
from .compat import string_types
from .compat import text_type
from .compat import asyncio
from .compat import Queue
import logging.config
import logging
import venusian
import signal
import time
import sys

try:
    import pkg_resources
except ImportError:  # pragma: no cover
    version = ''
else:
    version = pkg_resources.get_distribution('irc3').version


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
            self.close()
            # wait a few before reconnect
            self.factory.loop.call_later(
                2, self.factory.create_connection, self.__class__)

    def close(self):  # pragma: no cover
        if not self.closed:
            self.factory.log.critical('closing old transport (%r)',
                                      id(self.transport))
            try:
                self.transport.close()
            finally:
                self.closed = True


class IrcBot(object):
    """An IRC bot"""

    _pep8 = [event, extend, plugin, rfc, config]
    venusian = venusian
    venusian_categories = [
        'irc3.plugin',
        'irc3.extend',
        'irc3.rfc1459',
        'irc3.plugins.cron',
        'irc3.plugins.command',
    ]

    logging_config = config.LOGGING

    defaults = dict(
        nick='irc3',
        realname='irc3',
        userinfo='Irc bot based on irc3 http://irc3.readthedocs.org',
        host='irc.freenode.net',
        port=6667,
        ssl=False,
        timeout=320,
        max_lag=60,
        encoding='utf8',
        testing=False,
        async=True,
        max_length=512,
        version=version,
        url='https://irc3.readthedocs.org/',
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
        loop=None,
        connection=IrcConnection,
        categories=[]
    )

    def __init__(self, *ini, **config):
        self.config = utils.Config(dict(self.defaults, *ini, **config))
        logging.config.dictConfig(self.logging_config)
        self.log = logging.getLogger('irc3.' + self.nick)
        self.original_nick = self.nick
        if config.get('verbose'):
            logging.getLogger('irc3').setLevel(logging.DEBUG)
        else:
            level = config.get('level')
            if level is not None:
                level = getattr(logging, str(level), level)
                self.log.setLevel(level)
        self.encoding = self.config['encoding']

        self.loop = self.config.loop
        if self.loop is None:
            self.loop = asyncio.get_event_loop()

        self.events_re = {'in': [], 'out': []}
        self.events = {
            'in': defaultdict(list),
            'out': defaultdict(list)
        }

        self.venusian_categories.extend(self.config.get('categories'))

        self.plugins = {}
        self.includes = set()
        self.include(*self.config.get('includes', []))

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
        for iotype in ('in', 'out'):
            events_re = []
            for regexp, cregexp in self.events_re[iotype]:
                e = self.events[iotype][regexp][0]
                e.compile(self.config)
                events_re.append((regexp, e.cregexp))
            self.events_re[iotype] = events_re

    def attach_events(self, *events, **kwargs):
        """Attach one or more events to the bot instance"""
        for e in events:
            e.compile(self.config)
            regexp = getattr(e.regexp, 're', e.regexp)
            if regexp not in self.events[e.iotype]:
                if 'insert' in kwargs:
                    self.events_re[e.iotype].insert(0, (regexp, e.cregexp))
                else:
                    self.events_re[e.iotype].append((regexp, e.cregexp))
            if 'insert' in kwargs:
                self.events[e.iotype][regexp].insert(0, e)
            else:
                self.events[e.iotype][regexp].append(e)

    def detach_events(self, *events):
        """Detach one or more events from the bot instance"""
        for e in events:
            regexp = getattr(e.regexp, 're', e.regexp)
            if e in self.events[e.iotype].get(regexp, []):
                self.events[e.iotype][regexp].remove(e)
                if not self.events[e.iotype][regexp]:
                    del self.events[e.iotype][regexp]
                    events_re = self.events_re[e.iotype]
                    events_re = [r for r in events_re if r[0] != regexp]
                    self.events_re[e.iotype] = events_re

    def include(self, *modules, **kwargs):
        categories = kwargs.get('venusian_categories',
                                self.venusian_categories)
        scanner = self.venusian.Scanner(bot=self)
        for module in modules:
            if module in self.includes:
                self.log.warn('%s included twice', module)
            else:
                self.includes.add(module)
                scanner.scan(utils.maybedotted(module), categories=categories)

    def connection_made(self, f):  # pragma: no cover
        if getattr(self, 'protocol', None):
            self.protocol.close()
        try:
            transport, protocol = f.result()
        except Exception as e:
            self.log.exception(e)
            self.loop.call_later(3, self.create_connection)
        else:
            self.log.info('Connected')
            self.protocol = protocol
            self.protocol.queue = Queue(loop=self.loop)
            self.protocol.factory = self
            self.protocol.encoding = self.encoding
            if self.config.get('password'):
                self._send('PASS {password}'.format(**self.config))
            self._send((
                'USER {realname} {host} {host} :{userinfo}\r\n'
                'NICK {nick}\r\n').format(**self.config))
            self.notify('connection_made')

    def notify(self, event, exc=None):
        for p in self.plugins.values():
            meth = getattr(p, event, None)
            if meth is not None:
                meth()

    def dispatch(self, data, iotype='in'):
        events = []
        for regexp, cregexp in self.events_re[iotype]:
            match = cregexp.search(data)
            if match is not None:
                match = match.groupdict()
                for key, value in match.items():
                    if value is not None:
                        match[key] = IrcString(value)
                for e in self.events[iotype][regexp]:
                    self.loop.call_soon(e.async_callback, match)
                    events.append((e, match))
        return events

    def send(self, data):
        """send data to the server"""
        self._send(data)
        self.dispatch(data, iotype='out')

    def _send(self, data):
        # private method to avoid dispatch()
        self.log.debug('> %s', data.strip())
        self.protocol.write(data)

    def call_many(self, callback, args):
        """callback is run with each arg but run a call per second"""
        if isinstance(callback, string_types):
            callback = getattr(self, callback)
        i = 0
        for i, arg in enumerate(args):
            self.loop.call_later(i, callback, *arg)
        f = asyncio.Future()
        self.loop.call_later(i + 1, f.set_result, True)
        return f

    def privmsg(self, target, message):
        """send a privmsg to target"""
        if target and message:
            messages = utils.split_message(message, self.config.max_length)
            for message in messages:
                self.send('PRIVMSG %s :%s' % (target, message))

    def notice(self, target, message):
        """send a notice to target"""
        if target and message:
            messages = utils.split_message(message, self.config.max_length)
            for message in messages:
                self.send('NOTICE %s :%s' % (target, message))

    def ctcp(self, target, message):
        """send a ctcp to target"""
        if target and message:
            self.send('PRIVMSG %s :\x01%s\x01' % (target, message))

    def ctcp_reply(self, target, message):
        """send a ctcp reply to target"""
        if target and message:
            self.send('NOTICE %s :\x01%s\x01' % (target, message))

    def mode(self, target, *data):
        """set user or channel mode"""
        self.send('MODE %s %s' % (target, ' '.join(data)))

    def join(self, target):
        """join a channel"""
        self.send('JOIN %s' % target)

    def part(self, target, reason=None):
        """quit a channel"""
        if reason:
            target += ' :' + reason
        self.send('PART %s' % target)

    def kick(self, channel, target, reason=None):
        """kick target from channel"""
        if reason:
            target += ' :' + reason
        self.send('KICK %s %s' % (channel, target))

    def quit(self, reason=None):
        """disconnect"""
        if not reason:
            reason = 'bye'
        self.send('QUIT :%s' % reason)

    def get_nick(self):
        return self.config.nick

    def set_nick(self, nick):
        self.send('NICK ' + nick)

    nick = property(get_nick, set_nick, doc='nickname get/set')

    def create_connection(self):
        protocol = utils.maybedotted(self.config.connection)
        t = asyncio.Task(
            self.loop.create_connection(
                protocol, self.config.host,
                self.config.port, ssl=self.config.ssl),
            loop=self.loop)
        t.add_done_callback(self.connection_made)
        return self.loop

    def SIGHUP(self):
        self.quit('HUP')
        time.sleep(1)
        try:
            self.protocol.transport.close()
        finally:
            pass

    def SIGINT(self):
        self.notify('SIGINT')
        if getattr(self, 'protocol', None):
            self.quit('INT')
            time.sleep(1)
        self.loop.stop()

    def run(self, forever=True):
        """start the bot"""
        loop = self.create_connection()
        loop.add_signal_handler(signal.SIGHUP, self.SIGHUP)
        loop.add_signal_handler(signal.SIGINT, self.SIGINT)
        if forever:
            loop.run_forever()


def run(argv=None):
    """
    Run an irc bot from a config file

    Usage: irc3 [options] <config>...

    Options:

    --logdir DIRECTORY  Log directory to use instead of stderr
    --logdate           Show datetimes in console output
    -v,--verbose        Increase verbosity
    -r,--raw            Show raw irc log on the console
    -d,--debug          Add some debug commands/utils
    -i,--interactive    Load a ipython console with a bot instance
    --help-page         Output a reST page containing commands help
    """
    import os
    import docopt
    import textwrap
    args = argv or sys.argv[1:]
    args = docopt.docopt(textwrap.dedent(run.__doc__), args)
    cfg = utils.parse_config(*args['<config>'])
    cfg.update(
        verbose=args['--verbose'],
        debug=args['--debug'],
    )
    pythonpath = cfg.get('pythonpath', [])
    pythonpath.append(cfg['here'])
    for path in pythonpath:
        sys.path.append(os.path.expanduser(path))
    if args['--logdir'] or 'logdir' in cfg:
        logdir = os.path.expanduser(args['--logdir'] or cfg.get('logdir'))
        IrcBot.logging_config = config.get_file_config(logdir)
    if args['--logdate']:  # pragma: no cover
        fmt = IrcBot.logging_config['formatters']['console']
        fmt['format'] = config.TIMESTAMPED_FMT
    if args['--help-page']:  # pragma: no cover
        for v in IrcBot.logging_config['handlers'].values():
            v['level'] = 'ERROR'
    if args['--debug']:
        IrcBot.venusian_categories.append('irc3.debug')
    if args['--interactive']:  # pragma: no cover
        import irc3.testing
        bot = irc3.testing.IrcBot(**cfg)
    else:
        bot = IrcBot(**cfg)
    if args['--raw']:
        bot.include('irc3.plugins.log', venusian_categories=['irc3.debug'])
    if args['--help-page']:  # pragma: no cover
        bot.print_help_page()
    elif args['--interactive']:  # pragma: no cover
        import IPython
        IPython.embed()
    else:
        bot.run()
    if argv:
        return bot
