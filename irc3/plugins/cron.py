# -*- coding: utf-8 -*-
__doc__ = '''
==========================================
:mod:`irc3.plugins.cron` Cron plugin
==========================================

Introduce a ``@cron`` decorator

Create a python module with some crons:

.. literalinclude:: ../../examples/mycrons.py

..
    >>> import sys
    >>> sys.path.append('examples')
    >>> from testing import IrcBot

And register it::

    >>> bot = IrcBot()
    >>> bot.include('irc3.plugins.cron')    # register the plugin
    >>> bot.include('mycrons')            # register your crons

'''
from ..third.croniter import croniter
import functools
import venusian
import logging
import time
import irc3


class Cron(object):

    def __init__(self, cron, callback):
        self.cron = cron
        self.callback = callback
        self.croniter = None


@irc3.plugin
class Crons(list):

    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger(__name__)
        self.debug = self.log.getEffectiveLevel() == logging.DEBUG
        self.started = False

    def connection_made(self):
        if not self.started:
            self.start()

    def start(self):
        self.started = True
        self.time = time.time()
        self.loop_time = self.bot.loop.time()
        for cron in self:
            cron.croniter = croniter(cron.cron, self.time)
            self.log.debug('Starting {0.cron} {0.callback}'.format(cron))
            self.bot.loop.call_at(
                self.loop_time + (cron.croniter.get_next(float) - self.time),
                self.call_cron, cron)

    def call_cron(self, cron):
        try:
            cron.callback()
        except Exception as e:
            self.log.error('{0.cron} {0.callback}.'.format(cron))
            self.bot.log.exception(e)
        else:
            self.log.debug('{0.cron} {0.callback}.'.format(cron))
        self.bot.loop.call_at(
            self.loop_time + (cron.croniter.get_next(float) - self.time),
            self.call_cron, cron)

    def __repr__(self):
        return '<Crons ({})>'.format(len(self))


def cron(cronline, venusian_category='irc3.plugins.cron'):
    """main decorator"""
    def wrapper(func):
        def callback(context, name, ob):
            bot = context.bot
            crons = bot.get_plugin(Crons)
            if info.scope == 'class':
                callback = getattr(
                    bot.get_plugin(ob),
                    func.__name__)
            else:
                @functools.wraps(func)
                def wrapper(**kwargs):
                    return func(bot, **kwargs)
                callback = wrapper
            crons.append(Cron(cronline, callback))
        info = venusian.attach(func, callback, category=venusian_category)
        return func
    return wrapper
