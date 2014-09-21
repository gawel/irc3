# -*- coding: utf-8 -*-
from irc3 import dec
import venusian
import functools


def plugin(wrapped):
    """register a class as server plugin"""
    setattr(wrapped, '__irc3_plugin__', False)
    setattr(wrapped, '__irc3d_plugin__', True)
    return wrapped


class event(dec.event):
    """same as :class:`~irc3.dec.event` but for servers"""

    def __init__(self, regexp, *args, **kwargs):
        kwargs.setdefault('venusian_category', 'irc3d.rfc1459')
        regexp = getattr(regexp, 'server', None) or regexp
        super(event, self).__init__(regexp, *args, **kwargs)


def extend(func):
    """same as :func:`~irc3.dec.extend` but for servers"""
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
    info = venusian.attach(func, callback, category='irc3d.extend')
    return func
