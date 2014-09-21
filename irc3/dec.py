# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import functools
import venusian
import re


def plugin(wrapped):
    """register a class as plugin"""
    setattr(wrapped, '__irc3_plugin__', True)
    setattr(wrapped, '__irc3d_plugin__', False)
    return wrapped


class event(object):
    """register a method or function an irc event callback::

        >>> @event('^:\S+ 353 [^&#]+(?P<channel>\S+) :(?P<nicknames>.*)')
        ... def on_names(bot, channel=None, nicknames=None):
        ...     '''this will catch nickname when you enter a channel'''
        ...     print(channel, nicknames.split(':'))

    The callback can be either a function or a plugin method

    If you specify the `iotype` parameter to `"out"` then the event will be
    triggered when the regexp match something **sent** by the bot.

    For example this event will repeat private messages sent by the bot to the
    `#irc3` channel::

        >>> @event(r'PRIVMSG (?P<target>[^#]+) :(?P<data>.*)', iotype='out')
        ... def msg3(bot, target=None, data=None):
        ...     bot.privmsg('#irc3',
        ...                 '<{0}> {1}: {2}'.format(bot.nick, target, data))
    """

    venusian = venusian

    def __init__(self, regexp, callback=None, iotype='in',
                 venusian_category='irc3.rfc1459'):
        try:
            re.compile(getattr(regexp, 're', regexp))
        except Exception as e:
            raise e.__class__(str(e) + ' in ' + getattr(regexp, 're', regexp))
        self.regexp = regexp
        self.iotype = iotype
        self.callback = callback
        self.venusian_category = venusian_category

    def async_callback(self, kwargs):  # pragma: no cover
        return self.callback(**kwargs)

    def compile(self, config):
        regexp = getattr(self.regexp, 're', self.regexp)
        if config:
            regexp = regexp.format(**config)
        self.cregexp = re.compile(regexp)

    def __call__(self, wrapped):
        def callback(context, name, ob):
            obj = context.context
            if info.scope == 'class':
                self.callback = getattr(
                    obj.get_plugin(ob),
                    wrapped.__name__)
            else:
                @functools.wraps(wrapped)
                def wrapper(**kwargs):
                    return wrapped(obj, **kwargs)
                self.callback = wrapper
            # a new instance is needed to keep this related to *one* bot
            # instance
            e = self.__class__(self.regexp, self.callback,
                               venusian_category=self.venusian_category,
                               iotype=self.iotype)
            obj.attach_events(e)
        info = self.venusian.attach(wrapped, callback,
                                    category=self.venusian_category)
        return wrapped

    def __repr__(self):
        s = getattr(self.regexp, 'name', self.regexp)
        name = self.__class__.__name__
        return '<bound {0} {1} to {2}>'.format(name, s, self.callback)


def extend(func):
    """Allow to extend a bot:

    Create a module with some usefull routine:

    .. literalinclude:: ../examples/myextends.py
    ..
        >>> import sys
        >>> sys.path.append('examples')
        >>> from irc3 import IrcBot
        >>> IrcBot.defaults.update(async=False, testing=True)

    Now you can use those routine in your bot::

        >>> bot = IrcBot()
        >>> bot.include('myextends')
        >>> print(bot.my_usefull_function(1))
        my_usefull_function(*(1,))
        >>> print(bot.my_usefull_method(2))
        my_usefull_method(*(2,))

    """
    def callback(context, name, ob):
        obj = context.context
        if info.scope == 'class':
            @functools.wraps(func)
            def f(self, *args, **kwargs):
                plugin = obj.get_plugin(ob)
                return getattr(plugin, func.__name__)(*args, **kwargs)
            setattr(obj, func.__name__, f.__get__(obj, obj.__class__))
        else:
            setattr(obj, func.__name__, func.__get__(obj, obj.__class__))
    info = venusian.attach(func, callback, category='irc3.extend')
    return func
