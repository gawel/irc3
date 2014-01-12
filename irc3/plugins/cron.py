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
    >>> bot.include('mycrons')    # register your crons

'''
import functools
import venusian
import logging
import time
import irc3


class Cron(object):

    def __init__(self, cronline, callback, time=time.time()):
        self.cronline = cronline
        self.croniter = irc3.utils.maybedotted(
            'irc3.third.croniter.croniter'
        )(cronline, time)
        self.callback = callback

    def get_next(self):
        return self.croniter.get_next(float)

    def __call__(self):
        return self.callback()

    def __str__(self):
        return '{0.cronline} {0.callback}'.format(self)


@irc3.plugin
class Crons(list):

    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger(__name__)
        self.debug = self.log.getEffectiveLevel() == logging.DEBUG
        self.started = False
        self.time = time.time()
        self.loop_time = self.bot.loop.time()

    def connection_made(self):
        if not self.started:
            self.start()

    @irc3.extend
    def add_cron(self, cronline, callback):
        cron = Cron(cronline, callback, self.time)
        self.append(cron)
        if self.started:
            self.start_cron(cron)

    def start(self):
        self.started = True
        for cron in self:
            self.start_cron(cron)

    def start_cron(self, cron):
        self.log.debug('Starting {0}'.format(cron))
        self.bot.loop.call_at(
            self.loop_time + (cron.get_next() - self.time),
            self.call_cron, cron)

    def call_cron(self, cron):
        try:
            cron()
        except Exception as e:
            self.log.error(cron)
            self.bot.log.exception(e)
        else:
            self.log.debug(cron)
        self.bot.loop.call_at(
            self.loop_time + (cron.get_next() - self.time),
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
            crons.add_cron(cronline, callback)
        info = venusian.attach(func, callback, category=venusian_category)
        return func
    return wrapper
