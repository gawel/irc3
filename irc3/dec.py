# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import functools
import venusian
import re


def plugin(wrapped):
    """register a class as plugin"""
    def callback(context, name, ob):
        bot = context.bot
        for dotted in getattr(ob, 'requires', []):
            if dotted not in bot.includes:
                bot.include(dotted)
        bot.get_plugin(ob)
    assert isinstance(wrapped, type)
    venusian.attach(wrapped, callback, category='irc3.plugin')
    return wrapped


class event(object):
    """register a method or function an irc event callback::

        >>> @event('^:\S+ 353 [^&#]+(?P<channel>\S+) :(?P<nicknames>.*)')
        ... def on_names(self, channel=None, nicknames=None):
        ...     '''this will catch nickname when you enter a channel'''
        ...     print(channel, nicknames.split(':'))

    The callback can be either a function or a plugin method
    """

    venusian = venusian

    def __init__(self, regexp, callback=None, venusian_category=None):
        try:
            re.compile(getattr(regexp, 're', regexp))
        except Exception as e:
            raise e.__class__(str(e) + ' in ' + getattr(regexp, 're', regexp))
        self.regexp = regexp
        self.callback = callback
        self.venusian_category = venusian_category or 'irc3.rfc1459'

    def async_callback(self, kwargs):  # pragma: no cover
        return self.callback(**kwargs)

    def compile(self, config):
        regexp = getattr(self.regexp, 're', self.regexp)
        if config:
            regexp = regexp.format(**config)
        self.cregexp = re.compile(regexp)

    def __call__(self, wrapped):
        def callback(context, name, ob):
            bot = context.bot
            if info.scope == 'class':
                self.callback = getattr(
                    bot.get_plugin(ob),
                    wrapped.__name__)
            else:
                @functools.wraps(wrapped)
                def wrapper(**kwargs):
                    return wrapped(bot, **kwargs)
                self.callback = wrapper
            # a new instance is needed to keep this related to *one* bot
            # instance
            e = self.__class__(self.regexp, self.callback,
                               venusian_category=self.venusian_category)
            e.compile(bot.config)
            bot.add_event(e)
        info = self.venusian.attach(wrapped, callback,
                                    category=self.venusian_category)
        return wrapped

    def __repr__(self):
        s = getattr(self.regexp, 'name', self.regexp)
        return '<event %s>' % s


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
        bot = context.bot
        if info.scope == 'class':
            @functools.wraps(func)
            def f(self, *args, **kwargs):
                plugin = bot.get_plugin(ob)
                return getattr(plugin, func.__name__)(*args, **kwargs)
            setattr(bot, func.__name__, f.__get__(bot, bot.__class__))
        else:
            setattr(bot, func.__name__, func.__get__(bot, bot.__class__))
    info = venusian.attach(func, callback, category='irc3.extend')
    return func
