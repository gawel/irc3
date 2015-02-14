# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from irc3.compat import PY3
from irc3.compat import string_types
from irc3 import utils
from collections import defaultdict
import functools
import venusian
import fnmatch
import logging
import docopt
import irc3
import sys
__doc__ = '''
==========================================
:mod:`irc3.plugins.command` Command plugin
==========================================

Introduce a ``@command`` decorator

The decorator use `docopts <http://docopt.org/>`_ to parse command arguments.

Usage
=====

Create a python module with some commands:

.. literalinclude:: ../../examples/mycommands.py

..
    >>> import sys
    >>> sys.path.append('examples')
    >>> from irc3.testing import IrcBot
    >>> from irc3.testing import ini2config

And register it::

    >>> bot = IrcBot()
    >>> bot.include('irc3.plugins.command')  # register the plugin
    >>> bot.include('mycommands')            # register your commands


Check the result::

    >>> bot.test(':gawel!user@host PRIVMSG #chan :!echo foo')
    PRIVMSG gawel :foo

In the docstring, ``%%`` is replaced by the command character. ``!`` by
default. You can override it by passing a ``cmd`` parameter to bot's config.

When a command is not public, you can't use it on a channel::

    >>> bot.test(':gawel!user@host PRIVMSG #chan :!adduser foo pass')
    PRIVMSG gawel :You can only use the 'adduser' command in private.

Guard
=====

You can use a guard to prevent untrusted users to run some commands. The
:class:`free_policy` is used by default.

There is two builtin policy:

.. autoclass:: free_policy


.. autoclass:: mask_based_policy

Mask based guard using permissions::

    >>> config = ini2config("""
    ... [bot]
    ... includes =
    ...     irc3.plugins.command
    ...     mycommands
    ... [irc3.plugins.command]
    ... guard = irc3.plugins.command.mask_based_policy
    ... [irc3.plugins.command.masks]
    ... gawel!*@* = all_permissions
    ... foo!*@* = help
    ... """)
    >>> bot = IrcBot(**config)

foo is allowed to use command without permissions::

    >>> bot.test(':foo!u@h PRIVMSG nono :!echo got the power')
    PRIVMSG foo :got the power

foo is not allowed to use command except those with the help permission::

    >>> bot.test(':foo!u@h PRIVMSG nono :!ping')
    PRIVMSG foo :You are not allowed to use the 'ping' command

gawel is allowed::

    >>> bot.test(':gawel!u@h PRIVMSG nono :!ping')
    NOTICE gawel :PONG gawel!

Available options
=================

.. code-block:: ini

    [irc3.plugins.command]
    cmd = !
    antiflood = true
    guard = irc3.plugins.command.mask_based_policy

'''

WEIRD_CHARS = '$^|.*?'


class free_policy(object):
    """Default policy"""
    def __init__(self, bot):
        self.context = bot

    def __call__(self, predicates, meth, client, target, args, **kwargs):
        return meth(client, target, args)


class mask_based_policy(object):
    """Allow only valid masks. Able to take care or permissions"""

    key = __name__ + '.masks'

    def __init__(self, bot):
        self.context = bot
        self.log = logging.getLogger(__name__)
        self.log.debug('Masks: %r', self.masks)

    @property
    def masks(self):
        masks = self.context.config[self.key]
        if hasattr(self.context, 'db'):
            # update config with storage values
            value = self.context.db[self.key]
            if isinstance(value, dict):
                masks.update(value)
        return masks

    def has_permission(self, mask, permission):
        for pattern in self.masks:
            if fnmatch.fnmatch(mask, pattern):
                if permission is None or not isinstance(self.masks, dict):
                    return True
                perms = self.masks[pattern]
                if permission in perms or 'all_permissions' in perms:
                    return True
        return False

    def __call__(self, predicates, meth, client, target, args, **kwargs):
        if self.has_permission(client, predicates.get('permission')):
            return meth(client, target, args)
        cmd_name = predicates.get('name', meth.__name__)
        self.context.privmsg(
            client.nick,
            'You are not allowed to use the %r command' % cmd_name)


def attach_command(func, depth=2, **predicates):
    commands = predicates.pop('commands',
                              'irc3.plugins.command.Commands')
    category = predicates.pop('venusian_category',
                              'irc3.plugins.command')

    def callback(context, name, ob):
        obj = context.context
        if info.scope == 'class':
            callback = func.__get__(obj.get_plugin(ob), ob)
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(obj, *args, **kwargs)
            callback = wrapper
        plugin = obj.get_plugin(utils.maybedotted(commands))
        predicates.update(module=func.__module__)
        cmd_name = predicates.get('name', func.__name__)
        plugin[cmd_name] = (predicates, callback)
        obj.log.debug('Register command %r', cmd_name)
    info = venusian.attach(func, callback,
                           category=category, depth=depth)


def command(*func, **predicates):
    if func:
        func = func[0]
        attach_command(func, **predicates)
        return func
    else:
        def wrapper(func):
            attach_command(func, **predicates)
            return func
        return wrapper


@irc3.plugin
class Commands(dict):

    __reloadable__ = False

    requires = [
        __name__.replace('command', 'core'),
    ]
    default_policy = free_policy

    def __init__(self, context):
        self.context = context
        module = self.__class__.__module__
        self.config = config = context.config.get(module, {})
        self.log = logging.getLogger(module)
        self.log.debug('Config: %r', config)

        if 'cmd' in context.config:  # in case of
            config['cmd'] = context.config['cmd']
        context.config['cmd'] = self.cmd = config.get('cmd', '!')
        if self.cmd in WEIRD_CHARS:
            context.config['re_cmd'] = r'\%s' % self.cmd
        else:
            context.config['re_cmd'] = self.cmd

        self.antiflood = self.config.get('antiflood', False)

        guard = utils.maybedotted(config.get('guard', self.default_policy))
        self.log.debug('Guard: %s', guard.__name__)
        self.guard = guard(context)

        self.handles = defaultdict(Done)

    @irc3.event((r':(?P<mask>\S+) PRIVMSG (?P<target>\S+) '
                 r':{re_cmd}(?P<cmd>\w+)(\s(?P<data>\S.*)|$)'))
    def on_command(self, cmd, mask=None, target=None, client=None, **kw):
        predicates, meth = self.get(cmd, (None, None))
        if meth is not None:
            if predicates.get('public', True) is False and target.is_channel:
                self.context.privmsg(
                    mask.nick,
                    'You can only use the %r command in private.' % str(cmd))
            else:
                self.do_command(predicates, meth, mask, target, **kw)

    def do_command(self, predicates, meth, client, target, data=None, **kw):
        nick = self.context.nick or '-'
        to = target == nick and client.nick or target
        doc = meth.__doc__ or ''
        doc = [l.strip() for l in doc.strip().split('\n')]
        doc = [nick + ' ' + l.strip('%%')
               for l in doc if l.startswith('%%')]
        doc = 'Usage:' + '\n    ' + '\n    '.join(doc)
        encoding = self.context.encoding
        if data:
            if not isinstance(data, str):  # pragma: no cover
                data = data.encode(encoding)
        data = data and data.split() or []
        docopt_args = dict(help=False)
        if "options_first" in predicates:
            docopt_args.update(options_first=predicates["options_first"])
        cmd_name = predicates.get('name', meth.__name__)
        try:
            args = docopt.docopt(doc, [cmd_name] + data, **docopt_args)
        except docopt.DocoptExit:
            self.context.privmsg(to, 'Invalid arguments.')
        else:
            uid = (cmd_name, to)
            if not self.handles[uid].done() and self.antiflood:
                self.context.notice(
                    client if self.context.server else client.nick,
                    "Please be patient and don't flood me")
            else:
                if not PY3:
                    # back to unicode
                    for k, v in args.items():
                        if isinstance(v, list):
                            args[k] = [s.decode(encoding) for s in v]
                        elif v not in (None, True, False):
                            args[k] = v.decode(encoding)
                msgs = self.guard(predicates, meth, client, target, args=args)
                if msgs is not None:
                    def iterator(msgs):
                        for msg in msgs:
                            yield to, msg
                    if isinstance(msgs, string_types):
                        msgs = [msgs]
                    handle = self.context.call_many('privmsg', iterator(msgs))
                    self.handles[uid] = handle

    @command
    def help(self, mask, target, args):
        """Show help

            %%help [<cmd>]
        """
        if args['<cmd>']:
            predicates, meth = self.get(args['<cmd>'], (None, None))
            if meth is not None:
                doc = meth.__doc__ or ''
                doc = [l.strip() for l in doc.split('\n') if l.strip()]
                buf = ''
                for line in doc:
                    if '%%' not in line and buf is not None:
                        buf += line + ' '
                    else:
                        if buf is not None:
                            for b in utils.split_message(buf, 160):
                                yield b
                            buf = None
                        line = line.replace('%%', self.context.config.cmd)
                        yield line
        else:
            cmds = ', '.join([self.cmd + k for k in sorted(self.keys())])
            lines = utils.split_message('Available commands: ' + cmds, 160)
            for line in lines:
                yield line
            url = self.config.get('url')
            if url:
                yield 'Full help is available at ' + url

    def __repr__(self):
        return '<Commands %s>' % sorted([self.cmd + k for k in self.keys()])


class Done(object):

    def done(self):
        return True


@command(permission='admin', public=False)
def ping(bot, mask, target, args):
    """ping/pong

        %%ping
    """
    bot.send('NOTICE %(nick)s :PONG %(nick)s!' % dict(nick=mask.nick))


@command(venusian_category='irc3.debug')
def quote(bot, mask, target, args):
    """send quote to the server

        %%quote <args>...
    """
    msg = ' '.join(args['<args>'])
    bot.log.info('quote> %r', msg)
    bot.send(msg)


@command(venusian_category='irc3.debug')
def reconnect(bot, mask, target, args):
    """force reconnect

        %%reconnect
    """
    plugin = bot.get_plugin(utils.maybedotted('irc3.plugins.core.Core'))
    bot.loop.call_soon(plugin.reconnect)


@irc3.extend
def print_help_page(bot, file=sys.stdout):
    """print help page"""
    def p(text):
        print(text, file=file)
    plugin = bot.get_plugin(Commands)
    title = "Available Commands for {nick} at {host}".format(**bot.config)
    p("=" * len(title))
    p(title)
    p("=" * len(title))
    p('')
    p('.. contents::')
    p('')
    modules = {}
    for name, (predicates, callback) in plugin.items():
        commands = modules.setdefault(callback.__module__, [])
        commands.append((name, callback, predicates))

    for module in sorted(modules):
        p(module)
        p('=' * len(module))
        p('')
        for name, callback, predicates in sorted(modules[module]):
            p(name)
            p('-' * len(name))
            p('')
            doc = callback.__doc__
            doc = doc.replace('%%', bot.config.cmd)
            for line in doc.split('\n'):
                line = line.strip()
                if line.startswith(bot.config.cmd):
                    line = '    ``{}``'.format(line)
                p(line)
            if 'permission' in predicates:
                p('*Require {0[permission]} permission.*'.format(predicates))
            if predicates.get('public', True) is False:
                p('*Only available in private.*')
            p('')
