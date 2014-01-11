# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
__doc__ = '''
==========================================
:mod:`irc3.plugins.command` Command plugin
==========================================

Introduce a ``@command`` decorator

The decorator use `docopts <http://docopt.org/>`_ to parse command arguments.

Example:

Create a python module with some commands:

.. literalinclude:: ../../examples/mycommands.py

..
    >>> import sys
    >>> sys.path.append('examples')
    >>> from testing import IrcBot

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

You can use a guard to prevent untrusted users to run some commands. The
:class:`free_policy` is used by default.

There is two builtin policy:

.. autoclass:: free_policy


.. autoclass:: mask_based_policy

Guard usage::

    >>> config = {
    ...     'irc3.plugins.command': {'guard': mask_based_policy},
    ...     'irc3.plugins.command.masks': ['gawel!*@*']}
    >>> bot = IrcBot(**config)
    >>> bot.include('irc3.plugins.command')  # register the plugin
    >>> bot.include('mycommands')            # register your commands
    >>> bot.test(':foo!u@h PRIVMSG #chan :!echo bar')
    PRIVMSG foo :You are not allowed to use the 'echo' command
    >>> bot.test(':gawel!u@h PRIVMSG #chan :!echo bar')
    PRIVMSG gawel :bar

Mask based guard using permissions::

    >>> config = {
    ...     'nick': 'nono',
    ...     'irc3.plugins.command': {'guard': mask_based_policy},
    ...     'irc3.plugins.command.masks': {
    ...     'gawel!*@*': ['all_permissions'],
    ...     'foo!*@*': ['help'],
    ... }}
    >>> bot = IrcBot(**config)
    >>> bot.include('irc3.plugins.command')  # register the plugin
    >>> bot.test(':foo!u@h PRIVMSG nono :!ping')
    PRIVMSG foo :You are not allowed to use the 'ping' command
    >>> bot.test(':gawel!u@h PRIVMSG nono :!ping')
    NOTICE gawel :PONG gawel!

'''
from irc3.compat import string_types
from irc3 import utils
import functools
import venusian
import fnmatch
import logging
import docopt
import irc3
import sys


class free_policy(object):
    """Default policy"""
    def __init__(self, bot):
        self.bot = bot

    def __call__(self, predicates, meth, mask, target, args):
        return meth(mask, target, args)


class mask_based_policy(object):
    """Allow only valid masks. Able to take care or permissions"""
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger(__name__)
        self.masks = bot.config[__name__ + '.masks']
        self.log.debug('Masks: %r', self.masks)

    def has_permission(self, mask, permission):
        for pattern in self.masks:
            if fnmatch.fnmatch(mask, pattern):
                if permission is None or not isinstance(self.masks, dict):
                    return True
                perms = self.masks[pattern]
                if permission in perms or 'all_permissions' in perms:
                    return True
        return False

    def __call__(self, predicates, meth, mask, target, args):
        if self.has_permission(mask, predicates.get('permission')):
            return meth(mask, target, args)
        self.bot.privmsg(
            mask.nick,
            'You are not allowed to use the %r command' % meth.__name__
        )


class command(object):

    venusian = venusian
    defaults = {'permission': None}

    def __init__(self, *func, **predicates):
        self.predicates = predicates
        if func:
            self.__call__ = self.func = func[0]
            self.info = self.venusian.attach(self, self.callback,
                                             category=self.__module__)
        self.category = self.predicates.pop('venusian_category',
                                            self.__module__)

    def callback(self, context, name, ob):
        bot = context.bot
        if self.info.scope == 'class':
            callback = self.func.__get__(bot.get_plugin(ob), ob)
        else:
            @functools.wraps(self.func)
            def wrapper(*args, **kwargs):
                return self.func(bot, *args, **kwargs)
            callback = wrapper
        plugin = bot.get_plugin(Commands)
        self.predicates.update(module=self.func.__module__)
        plugin[self.func.__name__] = (self.predicates, callback)
        bot.log.info('Register command %r', self.func.__name__)

    def __call__(self, func):
        self.__call__ = self.func = func
        self.info = self.venusian.attach(func, self.callback,
                                         category=self.category)
        return func


@irc3.plugin
class Commands(dict):

    requires = [
        __name__.replace('command', 'core'),
    ]

    def __init__(self, bot):
        self.bot = bot
        self.config = config = bot.config.get(__name__, {})
        self.log = logging.getLogger(__name__)
        self.log.debug('Config: %r', config)
        bot.config['cmd'] = self.cmd = config.get('cmd', '!')
        guard = utils.maybedotted(config.get('guard', free_policy))
        self.log.debug('Guard: %s', guard.__name__)
        self.guard = guard(bot)

    @irc3.event((r':(?P<mask>\S+) PRIVMSG (?P<target>\S+) '
                 r':{cmd}(?P<cmd>\w+)(\s(?P<data>[-0-9A-z]+.*)|$)'))
    def on_command(self, cmd, mask=None, target=None, data=None, **kw):
        predicates, meth = self.get(cmd, (None, None))
        if meth is not None:
            if predicates.get('public', True) is False and target.is_channel:
                self.bot.privmsg(
                    mask.nick,
                    'You can only use the %r command in private.' % cmd)
            else:
                self.do_command(predicates, meth, mask, target, data)

    def do_command(self, predicates, meth, mask, target, data):
        nick = self.bot.nick
        to = target == nick and mask.nick or target
        doc = meth.__doc__ or ''
        doc = [l.strip() for l in doc.strip().split('\n')]
        doc = [nick + ' ' + l.strip('%%')
               for l in doc if l.startswith('%%')]
        doc = 'Usage:' + '\n    ' + '\n    '.join(doc)
        data = data and data.split() or []
        try:
            args = docopt.docopt(doc, [meth.__name__] + data, help=False)
        except docopt.DocoptExit:
            self.bot.privmsg(to, 'Invalid arguments.')
        else:
            msgs = self.guard(predicates, meth, mask, target, args)
            if msgs is not None:
                def iterator(msgs):
                    for msg in msgs:
                        yield to, msg
                if isinstance(msgs, string_types):
                    msgs = [msgs]
                self.bot.call_many('privmsg', iterator(msgs))

    @command(permission='view')
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
                        line = line.replace('%%', self.bot.config.cmd)
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
