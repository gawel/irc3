# -*- coding: utf-8 -*-
import sys
import ssl
import signal
import logging
import logging.config
from . import utils
from . import config
from .compat import asyncio
from .compat import reload_module
from .compat import string_types
from collections import defaultdict

try:
    import pkg_resources
except ImportError:  # pragma: no cover
    version = ''
else:
    version = pkg_resources.get_distribution('irc3').version


class IrcObject(object):

    nick = None
    server = False
    logging_config = config.LOGGING

    defaults = dict(
        port=6667,
        timeout=320,
        max_lag=60,
        async=True,
        max_length=512,
        testing=False,
        ssl=False,
        ssl_verify=False,
        encoding='utf8',
        loop=None,
    )

    def __init__(self, *ini, **config):
        config['version'] = version
        self.config = utils.Config(dict(self.defaults, *ini, **config))
        logging.config.dictConfig(self.logging_config)
        if self.server:
            self.log = logging.getLogger('irc3d')
        else:
            self.log = logging.getLogger('irc3.' + (self.nick or 'd'))
        self.original_nick = self.nick
        if config.get('verbose') or config.get('debug'):
            logging.getLogger('irc3').setLevel(logging.DEBUG)
            logging.getLogger('irc3d').setLevel(logging.DEBUG)
        else:
            level = config.get('level')
            if level is not None:
                level = getattr(logging, str(level), level)
                self.log.setLevel(level)
        self.encoding = self.config['encoding']

        self.loop = self.config.loop
        if self.loop is None:
            self.loop = asyncio.get_event_loop()

        self.reset()

        self.include(*self.config.get('includes', []))

        # auto include the autojoins plugin if needed (for backward compat)
        if 'autojoins' in self.config and \
           'irc3.plugins.autojoins' not in self.includes:
            self.include('irc3.plugins.autojoins')

        self.recompile()

    def reset(self, reloading=False):
        self.events_re = {'in': [], 'out': []}
        self.events = {
            'in': defaultdict(list),
            'out': defaultdict(list)
        }

        self.scanned = []
        self.includes = set()

        if reloading:
            self.reloading = self.plugins.copy()
        else:
            self.reloading = {}
            self.plugins = {}

    def get_plugin(self, ob):
        if isinstance(ob, string_types):
            ob_name = ob
            ob = utils.maybedotted(ob_name)
            if ob_name not in self.plugins:
                names = list(self.plugins)
                raise LookupError(
                    'Plugin %s not found in %s' % (ob_name, names))
        else:
            ob_name = ob.__module__ + '.' + ob.__name__
        if ob_name not in self.plugins:
            self.log.debug("Register plugin '%s'", ob_name)
            for dotted in getattr(ob, 'requires', []):
                if dotted not in self.includes:
                    self.include(dotted)
            self.plugins[ob_name] = ob(self)
        elif ob_name in self.reloading and hasattr(ob, 'reload'):
                instance = self.reloading.pop(ob_name)
                if instance.__class__ is not ob:
                    self.log.debug("Reloading plugin '%s'", ob_name)
                    self.plugins[ob_name] = ob.reload(instance)
        return self.plugins[ob_name]

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
        plugin_category = '__irc3_plugin__'
        if self.server:
            plugin_category = '__irc3d_plugin__'
        categories = kwargs.get('venusian_categories',
                                self.venusian_categories)
        scanner = self.venusian.Scanner(context=self)
        for module in modules:
            if module in self.includes:
                self.log.warn('%s included twice', module)
            else:
                self.includes.add(module)
                module = utils.maybedotted(module)
                # we have to manualy check for plugins. venusian no longer
                # support to attach both a class and methods
                for klass in module.__dict__.values():
                    if not isinstance(klass, type):
                        continue
                    if klass.__module__ == module.__name__:
                        if getattr(klass, plugin_category, False) is True:
                            self.get_plugin(klass)
                self.scanned.append((module.__name__, categories))
                scanner.scan(module, categories=categories)

    def reload(self, *modules):
        """Reload one or more plugins"""
        self.notify('before_reload')

        if 'configfiles' in self.config:
            # reload configfiles
            self.log.info('Reloading configuration...')
            cfg = utils.parse_config(
                self.server and 'server' or 'bot', *self.config['configfiles'])
            self.config.update(cfg)

        self.log.info('Reloading python code...')
        if not modules:
            modules = self.includes
        scanned = list(reversed(self.scanned))

        # reset includes and events
        self.reset(reloading=True)

        to_scan = []
        for module, categories in scanned:
            if module in modules:
                module = utils.maybedotted(module)
                module = reload_module(module)
            to_scan.append((module, categories))

        # rescan all modules
        for module, categories in to_scan:
            self.include(module, venusian_categories=categories)

        self.reloading = {}

        self.notify('after_reload')

    def notify(self, event, exc=None, client=None):
        for p in self.plugins.values():
            meth = getattr(p, event, None)
            if meth is not None:
                if client is not None:
                    meth(client=client)
                else:
                    meth()

    def dispatch(self, data, iotype='in', client=None):
        events = []
        for regexp, cregexp in self.events_re[iotype]:
            match = cregexp.search(data)
            if match is not None:
                match = match.groupdict()
                for key, value in match.items():
                    if value is not None:
                        match[key] = utils.IrcString(value)
                if client is not None:
                    # server
                    match['client'] = client
                for e in self.events[iotype][regexp]:
                    self.loop.call_soon(e.async_callback, match)
                    events.append((e, match))
        return events

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

    def get_ssl_context(self):
        if self.config.ssl:  # pragma: no cover
            try:
                create_default_context = ssl.create_default_context
            except AttributeError:  # py < 2.7.9
                return True
            else:
                if self.server:
                    context = create_default_context(ssl.Purpose.SERVER_AUTH)
                else:
                    context = create_default_context(ssl.Purpose.CLIENT_AUTH)
                verify_mode = self.config.ssl_verify
                if verify_mode is not False:
                    if not isinstance(verify_mode, int):
                        # CERT_NONE / CERT_OPTIONAL / CERT_REQUIRED
                        verify_mode = getattr(ssl, verify_mode.upper())
                    context.verify_mode = verify_mode
                return context
        return None

    def create_connection(self):
        protocol = utils.maybedotted(self.config.connection)
        protocol = type(protocol.__name__, (protocol,), {'factory': self})
        if self.server:  # pragma: no cover
            self.log.debug('Starting {servername}...'.format(**self.config))
            factory = self.loop.create_server
        else:
            self.log.debug('Starting {nick}...'.format(**self.config))
            factory = self.loop.create_connection
        t = asyncio.Task(
            factory(
                protocol, self.config.host,
                self.config.port, ssl=self.get_ssl_context()),
            loop=self.loop)
        t.add_done_callback(self.connection_made)
        return self.loop

    def run(self, forever=True):
        """start the bot"""
        loop = self.create_connection()
        loop.add_signal_handler(signal.SIGHUP, self.SIGHUP)
        loop.add_signal_handler(signal.SIGINT, self.SIGINT)
        if forever:
            loop.run_forever()

    @classmethod
    def from_argv(cls, argv=None, **kwargs):
        prog = cls.server and 'irc3d' or 'irc3'
        doc = """
        Run an {prog} instance from a config file

        Usage: {prog} [options] <config>...

        Options:

        --logdir DIRECTORY  Log directory to use instead of stderr
        --logdate           Show datetimes in console output
        -v,--verbose        Increase verbosity
        -r,--raw            Show raw irc log on the console
        -d,--debug          Add some debug commands/utils
        -i,--interactive    Load a ipython console with a bot instance
        """.format(prog=prog)
        if not cls.server:
            doc += """
            --help-page         Output a reST page containing commands help
            """.strip()
        import os
        import docopt
        import textwrap
        args = argv or sys.argv[1:]
        args = docopt.docopt(textwrap.dedent(doc), args)
        cfg = utils.parse_config(
            cls.server and 'server' or 'bot', *args['<config>'])
        cfg.update(kwargs)
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
            cls.logging_config = config.get_file_config(logdir)
        if args['--logdate']:  # pragma: no cover
            fmt = cls.logging_config['formatters']['console']
            fmt['format'] = config.TIMESTAMPED_FMT
        if args.get('--help-page'):  # pragma: no cover
            for v in cls.logging_config['handlers'].values():
                v['level'] = 'ERROR'
        if args['--debug']:
            cls.venusian_categories.append(prog + '.debug')
        if args['--interactive']:  # pragma: no cover
            import irc3.testing
            context = getattr(irc3.testing, cls.__name__)(**cfg)
        else:
            context = cls(**cfg)
        if args['--raw']:
            context.include('irc3.plugins.log',
                            venusian_categories=[prog + '.debug'])
        if args.get('--help-page'):  # pragma: no cover
            context.print_help_page()
        elif args['--interactive']:  # pragma: no cover
            import IPython
            IPython.embed()
            sys.exit(0)
        else:
            context.run(forever=not bool(kwargs))
        if argv or kwargs:
            return context
