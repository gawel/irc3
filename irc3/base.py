# -*- coding: utf-8 -*-
import os
import sys
import ssl
import signal
import logging
import logging.config
from . import utils
from . import config
from .compat import asyncio
from .compat import reload_module
from collections import defaultdict

try:
    import pkg_resources
    from pkg_resources import iter_entry_points
    HAS_PKG_RESOURCES = True
except ImportError:  # pragma: no cover
    HAS_PKG_RESOURCES = False
    version = ''
else:
    try:
        version = pkg_resources.get_distribution('irc3').version
    except pkg_resources.DistributionNotFound:
        version = ''


class Registry:
    """Store (and hide from api) plugins events and stuff"""

    def __init__(self):
        self.reset(reloading=False)

    def reset(self, reloading=True):
        self.events_re = {
            'in': [], 'out': [],
            'dcc_in': [], 'dcc_out': [],
        }
        self.events = {
            'in': defaultdict(list),
            'out': defaultdict(list),
            'dcc_in': defaultdict(list),
            'dcc_out': defaultdict(list),
        }

        self.scanned = []
        self.includes = set()

        if reloading:
            self.reloading = self.plugins.copy()
        else:
            self.reloading = {}
            self.plugins = {}

    def get_event_matches(self, data, iotype='in'):
        events = self.events[iotype]
        for regexp, cregexp in self.events_re[iotype]:
            match = cregexp(data)
            if match is not None:
                yield match, events[regexp]


class IrcObject:

    nick = None
    server = False
    plugin_category = '__irc3_plugin__'
    logging_config = config.LOGGING

    defaults = dict(
        port=6667,
        timeout=320,
        max_lag=60,
        asynchronous=True,
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
            try:
                self.loop = asyncio.get_event_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)

        # python 3.4.1 do not have a create_task method. check for it
        self.create_task = getattr(self.loop, 'create_task', self.create_task)

        self.registry = Registry()

        self.include(*self.config.get('includes', []))

    def create_task(self, coro):  # pragma: no cover
        # python 3.4.1 fallback
        return asyncio.ensure_future(coro, loop=self.loop)

    def get_plugin(self, ob):
        plugins = self.registry.plugins
        includes = self.registry.includes
        reloading = self.registry.reloading

        if isinstance(ob, str):
            ob_name = ob
            ob = utils.maybedotted(ob_name)
            if ob_name not in plugins:
                names = list(plugins)
                raise LookupError(
                    'Plugin %s not found in %s' % (ob_name, names))
        else:
            ob_name = ob.__module__ + '.' + ob.__name__
        if ob_name not in plugins:
            self.log.debug("Register plugin '%s'", ob_name)
            for dotted in getattr(ob, 'requires', []):
                if dotted not in includes:
                    self.include(dotted)
            plugins[ob_name] = ob(self)
        elif ob_name in reloading and hasattr(ob, 'reload'):
                instance = reloading.pop(ob_name)
                if instance.__class__ is not ob:
                    self.log.debug("Reloading plugin '%s'", ob_name)
                    plugins[ob_name] = ob.reload(instance)
        return plugins[ob_name]

    def recompile(self):
        events_re = self.registry.events_re
        for iotype in ('in', 'out'):
            events = self.registry.events[iotype]
            for i, (regexp, cregexp) in enumerate(events_re[iotype]):
                e = events[regexp][0]
                events_re[i] = (regexp, e.compile(self.config))

    def attach_events(self, *events, **kwargs):
        """Attach one or more events to the bot instance"""
        reg = self.registry
        insert = 'insert' in kwargs
        for e in events:
            cregexp = e.compile(self.config)
            regexp = getattr(e.regexp, 're', e.regexp)
            if regexp not in reg.events[e.iotype]:
                if insert:
                    reg.events_re[e.iotype].insert(0, (regexp, cregexp))
                else:
                    reg.events_re[e.iotype].append((regexp, cregexp))
            if insert:
                reg.events[e.iotype][regexp].insert(0, e)
            else:
                reg.events[e.iotype][regexp].append(e)

    def detach_events(self, *events):
        """Detach one or more events from the bot instance"""
        reg = self.registry
        delete = defaultdict(list)

        # remove from self.events
        all_events = reg.events
        for e in events:
            regexp = getattr(e.regexp, 're', e.regexp)
            iotype = e.iotype
            if e in all_events[iotype].get(regexp, []):
                all_events[iotype][regexp].remove(e)
                if not all_events[iotype][regexp]:
                    del all_events[iotype][regexp]
                    # need to delete from self.events_re
                    delete[iotype].append(regexp)

        # delete from events_re
        for iotype, regexps in delete.items():
            reg.events_re[iotype] = [r for r in reg.events_re[iotype]
                                     if r[0] not in regexps]

    def include(self, *modules, **kwargs):
        reg = self.registry
        categories = kwargs.get('venusian_categories',
                                self.venusian_categories)
        scanner = self.venusian.Scanner(context=self)
        for module in modules:
            if module in reg.includes:
                self.log.warn('%s included twice', module)
            else:
                reg.includes.add(module)
                try:
                    module = utils.maybedotted(module)
                except LookupError as exc:
                    if HAS_PKG_RESOURCES:
                        entry_points = iter_entry_points(
                            'irc3.loader',
                            module
                        )
                        try:
                            module = next(entry_points).load()
                        except StopIteration:
                            raise exc
                    else:
                        raise exc
                # we have to manualy check for plugins. venusian no longer
                # support to attach both a class and methods
                for klass in list(module.__dict__.values()):
                    if not isinstance(klass, type):
                        continue
                    if klass.__module__ == module.__name__:
                        if getattr(klass, self.plugin_category, False) is True:
                            self.get_plugin(klass)
                reg.scanned.append((module.__name__, categories))
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
            modules = self.registry.includes
        scanned = list(reversed(self.registry.scanned))

        # reset includes and events
        self.registry.reset()

        to_scan = []
        for module_name, categories in scanned:
            if module_name in modules:
                module = utils.maybedotted(module_name)
                reload_module(module)
            to_scan.append((module_name, categories))

        # rescan all modules
        for module_name, categories in to_scan:
            self.include(module_name, venusian_categories=categories)

        self.registry.reloading = {}

        self.notify('after_reload')

    def notify(self, event, exc=None, client=None):
        for p in self.registry.plugins.values():
            meth = getattr(p, event, None)
            if meth is not None:
                if client is not None:
                    meth(client=client)
                else:
                    meth()

    def dispatch(self, data, iotype='in', client=None):
        str = utils.IrcString
        create_task = self.create_task
        call_soon = self.loop.call_soon
        for match, events in self.registry.get_event_matches(data, iotype):
            match = match.groupdict()
            for key, value in match.items():
                if value is not None:
                    match[key] = str(value)
            # backwards compatibility fix for IRCv3.2 tag support:
            # If no tags (None-value), exclude from dictionary
            if match.get("tags", True) is None:
                del match["tags"]
            if client is not None:
                # server / dcc chat
                match['client'] = client
            for e in events:
                if e.iscoroutine is True:
                    create_task(e.callback(**match))
                else:
                    call_soon(e.async_callback, match)

    def call_many(self, callback, args):
        """callback is run with each arg but run a call per second"""
        if isinstance(callback, str):
            callback = getattr(self, callback)
        f = None
        for arg in args:
            f = callback(*arg)
        return f

    def get_ssl_context(self):
        if self.config.ssl:  # pragma: no cover
            try:
                create_default_context = ssl.create_default_context
            except AttributeError:  # py < 2.7.9
                return True
            else:
                if self.server:
                    context = create_default_context(ssl.Purpose.CLIENT_AUTH)
                else:
                    context = create_default_context(ssl.Purpose.SERVER_AUTH)
                verify_mode = self.config.ssl_verify
                if verify_mode is not False:
                    if not isinstance(verify_mode, int):
                        # CERT_NONE / CERT_OPTIONAL / CERT_REQUIRED
                        verify_mode = getattr(ssl, verify_mode.upper())
                    if verify_mode == ssl.CERT_NONE:
                        context.check_hostname = False
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
        if self.config.get('sock_factory'):
            sock_factory = utils.maybedotted(self.config.sock_factory)
            args = dict(
                sock=sock_factory(self, self.config.host, self.config.port)
            )
        else:
            args = dict(
                host=self.config.host,
                port=self.config.port,
                ssl=self.get_ssl_context()
            )
            if self.config.get('vhost'):
                args["local_addr"] = (self.config.vhost, 0)
        t = asyncio.Task(factory(protocol, **args), loop=self.loop)
        t.add_done_callback(self.connection_made)
        return self.loop

    def add_signal_handlers(self):
        """Register handlers for UNIX signals (SIGHUP/SIGINT)"""
        try:
            self.loop.add_signal_handler(signal.SIGHUP, self.SIGHUP)
        except (RuntimeError, AttributeError):  # pragma: no cover
            # windows
            pass
        try:
            self.loop.add_signal_handler(signal.SIGINT, self.SIGINT)
        except (RuntimeError, NotImplementedError):  # pragma: no cover
            # annaconda
            pass

    def run(self, forever=True):
        """start the bot"""
        loop = self.create_connection()
        self.add_signal_handlers()
        if forever:
            loop.run_forever()

    @classmethod
    def from_config(cls, cfg, **kwargs):
        """return an instance configured with the ``cfg`` dict"""
        cfg = dict(cfg, **kwargs)
        pythonpath = cfg.get('pythonpath', [])
        if 'here' in cfg:
            pythonpath.append(cfg['here'])
        for path in pythonpath:
            sys.path.append(os.path.expanduser(path))
        prog = cls.server and 'irc3d' or 'irc3'
        if cfg.get('debug'):
            cls.venusian_categories.append(prog + '.debug')
        if cfg.get('interactive'):  # pragma: no cover
            import irc3.testing
            context = getattr(irc3.testing, cls.__name__)(**cfg)
        else:
            context = cls(**cfg)
        if cfg.get('raw'):
            context.include('irc3.plugins.log',
                            venusian_categories=[prog + '.debug'])
        return context

    @classmethod
    def from_argv(cls, argv=None, **kwargs):
        prog = cls.server and 'irc3d' or 'irc3'
        doc = """
        Run an {prog} instance from a config file

        Usage: {prog} [options] <config>...

        Options:

        -h, --help          Display this help and exit
        --version           Output version information and exit
        --logdir DIRECTORY  Log directory to use instead of stderr
        --logdate           Show datetimes in console output
        --host HOST         Server name or ip
        --port PORT         Server port
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
        args = docopt.docopt(textwrap.dedent(doc), args, version=version)
        cfg = utils.parse_config(
            cls.server and 'server' or 'bot', *args['<config>'])
        cfg.update(
            verbose=args['--verbose'],
            debug=args['--debug'],
        )
        cfg.update(kwargs)
        if args['--host']:  # pragma: no cover
            host = args['--host']
            cfg['host'] = host
            if host in ('127.0.0.1', 'localhost'):
                cfg['ssl'] = False
        if args['--port']:  # pragma: no cover
            cfg['port'] = args['--port']
        if args['--logdir'] or 'logdir' in cfg:
            logdir = os.path.expanduser(args['--logdir'] or cfg.get('logdir'))
            cls.logging_config = config.get_file_config(logdir)
        if args['--logdate']:  # pragma: no cover
            fmt = cls.logging_config['formatters']['console']
            fmt['format'] = config.TIMESTAMPED_FMT
        if args.get('--help-page'):  # pragma: no cover
            for v in cls.logging_config['handlers'].values():
                v['level'] = 'ERROR'
        if args['--raw']:
            cfg['raw'] = True
        context = cls.from_config(cfg)
        if args.get('--help-page'):  # pragma: no cover
            context.print_help_page()
        elif args['--interactive']:  # pragma: no cover
            import IPython
            IPython.embed()
            sys.exit(0)
        else:
            context.run(forever=not bool(kwargs))
        if kwargs or argv:
            return context
