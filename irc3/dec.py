# -*- coding: utf-8 -*-
from irc3.utils import wraps_with_context
from irc3.compat import asyncio
import venusian
import re


def plugin(wrapped):
    """register a class as plugin"""
    setattr(wrapped, '__irc3_plugin__', True)
    setattr(wrapped, '__irc3d_plugin__', False)
    return wrapped


class event:
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
        self.iscoroutine = False
        if callback is not None:
            self.iscoroutine = asyncio.iscoroutinefunction(callback)

    def async_callback(self, kwargs):  # pragma: no cover
        return self.callback(**kwargs)

    def compile(self, config):
        regexp = getattr(self.regexp, 're', self.regexp)
        if config:
            regexp = regexp.format(**config)
        return re.compile(regexp).match

    def __call__(self, func):
        def callback(context, name, ob):
            obj = context.context
            if info.scope == 'class':
                self.callback = getattr(obj.get_plugin(ob), func.__name__)
            else:
                self.callback = wraps_with_context(func, obj)
            # a new instance is needed to keep this related to *one* bot
            # instance
            e = self.__class__(self.regexp, self.callback,
                               venusian_category=self.venusian_category,
                               iotype=self.iotype)
            obj.attach_events(e)
        info = self.venusian.attach(func, callback,
                                    category=self.venusian_category)
        return func

    def __repr__(self):
        s = getattr(self.regexp, 'name', self.regexp)
        name = self.__class__.__name__
        return '<bound {0} {1} to {2}>'.format(name, s, self.callback)


def dcc_event(regexp, callback=None, iotype='in',
              venusian_category='irc3.dcc'):
    """Work like :class:`~irc3.dec.event` but occurs during DCC CHATs"""
    return event(regexp, callback=callback, iotype='dcc_' + iotype,
                 venusian_category=venusian_category)


def extend(func):
    """Allow to extend a bot:

    Create a module with some useful routine:

    .. literalinclude:: ../examples/myextends.py
    ..
        >>> import sys
        >>> sys.path.append('examples')
        >>> from irc3 import IrcBot
        >>> IrcBot.defaults.update(asynchronous=False, testing=True)

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
            f = getattr(obj.get_plugin(ob), func.__name__)
        else:
            f = func
        setattr(obj, f.__name__, f.__get__(obj, obj.__class__))
    info = venusian.attach(func, callback, category='irc3.extend')
    return func
