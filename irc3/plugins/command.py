# -*- coding: utf-8 -*-
__doc__ = '''
==========================================
:mod:`irc3.plugin.command` Command plugin
==========================================

Introduce a ``@command`` decorator

The decorator use `docopts <http://docopt.org/>`_ to parse command arguments.

Example:

Create a python module with some commands:

.. literalinclude:: ../../examples/mycommands.py

..
    >>> import sys
    >>> sys.path.append('examples')

And register it::

    >>> from irc3 import IrcBot
    >>> bot = IrcBot(cmd='$', async=False)
    >>> bot.include('irc3.plugins.command')  # register the plugin
    >>> bot.include('mycommands')            # register your commands

``%%`` is replaced by the command character. ``!`` by default. You can override
it by passing a ``cmd`` parameter to bot's config::


You can use a guard to prevent untrusted users to run some commands. The
:class:`free_policy` is used by default.

There is two builtin policy:

.. autoclass:: free_policy


.. autoclass:: mask_based_policy

Guard usage::

    >>> config = {'cmd.guard': mask_based_policy, 'cmd.masks': ['gawel!*@*']}
    >>> bot = IrcBot(**config)
    >>> bot.include('irc3.plugins.command')  # register the plugin
    >>> bot.include('mycommands')            # register your commands

'''
from irc3 import event
import functools
import venusian
import fnmatch
import docopt


class free_policy:
    """Default policy"""
    def __init__(self, bot):
        self.bot = bot

    def __call__(self, meth, mask, target, args):
        return meth(mask, target, args)


class mask_based_policy:
    """Allow only valid masks"""
    def __init__(self, bot):
        self.bot = bot
        self.masks = bot.config['cmd.masks']

    def __call__(self, meth, mask, target, args):
        for pattern in self.masks:
            if fnmatch.fnmatch(mask, pattern):
                return meth(mask, target, args)
        self.bot.privmsg(
            mask.nick,
            'You are not allowed to use the %r command' % meth.__name__
        )


def command(wrapped):
    def callback(context, name, ob):
        bot = context.bot
        if info.scope == 'class':
            callback = getattr(
                bot.get_plugin(ob),
                wrapped.__name__)
        else:
            @functools.wraps(wrapped)
            def wrapper(*args, **kwargs):
                return wrapped(bot, *args, **kwargs)
            callback = wrapper
        plugin = bot.get_plugin(Commands)
        plugin[callback.__name__] = callback
        bot.log.info('Register command %r', callback.__name__)
    info = venusian.attach(wrapped, callback,
                           category='irc3.plugin.command')
    return wrapped


class Commands(dict):

    def __init__(self, bot):
        self.bot = bot
        bot.config['cmd'] = self.cmd = bot.config.get('cmd', '!')
        guard = bot.config.get('cmd.guard', free_policy)
        self.guard = guard(bot)
        bot.log.info('Use %r as security guard', guard.__name__)

    @event((r':(?P<mask>\S+) PRIVMSG (?P<target>\S+) '
            r':%(cmd)s(?P<cmd>\w+)(\s(?P<data>\w+.*)|$)'))
    def on_command(self, cmd, mask=None, target=None, data=None, **kw):
        nick = self.bot.nick
        to = target == nick and mask.nick or target
        meth = self.get(cmd)
        if meth is not None:
            doc = meth.__doc__ or ''
            doc = [l.strip() for l in doc.strip().split('\n')]
            doc = [nick + ' ' + l.strip('%%')
                   for l in doc if l.startswith('%%')]
            doc = 'Usage:' + '\n    ' + '\n    '.join(doc)
            data = data and data.split() or []
            try:
                args = docopt.docopt(doc, [cmd] + data, help=False)
            except docopt.DocoptExit:
                self.bot.privmsg(to, 'Invalid arguments')
            else:
                msg = self.guard(meth, mask, target, args)
                self.bot.privmsg(to, msg)

    @command
    def help(self, mask, target, args):
        """Show help

            %%help [<cmd>]
        """
        to = target == self.bot.nick and mask.nick or target
        if args['<cmd>']:
            meth = self.get(args['<cmd>'])
            if meth is not None:
                doc = meth.__doc__ or ''
                doc = [l.strip() for l in doc.split('\n') if l.strip()]
                for line in doc:
                    line = line.replace('%%', self.bot.config.cmd)
                    self.bot.privmsg(to, line)
        else:
            nb = int(self.bot.config.get('help.item_per_line', 8))
            cmds = sorted([self.cmd + k for k in self.keys()])
            msg = ', '.join(cmds[0:nb - 3])
            self.bot.privmsg(to, 'Available commands: ' + msg)
            for x in range(nb - 3, len(cmds), nb):
                msg = ', '.join(cmds[x:x+nb])
                self.bot.privmsg(to, msg)

    def __repr__(self):
        return '<Commands %s>' % sorted([self.cmd + k for k in self.keys()])


@command
def ping(bot, mask, target, args):
    """ping/pong

        %%ping
    """
    bot.send('NOTICE %(nick)s :PONG %(nick)s!' % dict(nick=mask.nick))
