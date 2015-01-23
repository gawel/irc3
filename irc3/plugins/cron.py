# -*- coding: utf-8 -*-
__doc__ = '''
==========================================
:mod:`irc3.plugins.cron` Cron plugin
==========================================

Introduce a ``@cron`` decorator

Install croniter::

    $ pip install croniter

Create a python module with some crons:

.. literalinclude:: ../../examples/mycrons.py

..
    >>> import sys
    >>> sys.path.append('examples')
    >>> from irc3.testing import IrcBot

And register it::

    >>> bot = IrcBot()
    >>> bot.include('mycrons')    # register your crons

'''
from uuid import uuid4
import functools
import venusian
import logging
import time
import irc3


class Cron(object):

    def __init__(self, cronline, callback, time=time.time(), uuid=None):
        self.cronline = cronline
        self.croniter = irc3.utils.maybedotted(
            'croniter.croniter.croniter'
        )(cronline, time)
        self.callback = callback
        self.uuid = uuid or str(uuid4())

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
        self.handles = {}

    def connection_made(self):
        if not self.started:
            self.start()

    @irc3.extend
    def add_cron(self, cronline, callback, uuid=None):
        cron = Cron(cronline, callback, self.time, uuid=uuid)
        self.append(cron)
        if self.started:
            self.start_cron(cron)
        return cron

    @irc3.extend
    def remove_cron(self, cron=None, uuid=None):
        if uuid is None:
            uuid = cron.uuid
        if uuid in self.handles:
            handle = self.handles.pop(uuid)
            handle.cancel()

    def start(self):
        self.started = True
        for cron in self:
            self.start_cron(cron)

    def start_cron(self, cron):
        self.log.debug('Starting {0}'.format(cron))
        handle = self.bot.loop.call_at(
            self.loop_time + (cron.get_next() - self.time),
            self.call_cron, cron)
        self.handles[cron.uuid] = handle

    def call_cron(self, cron):
        try:
            cron()
        except Exception as e:
            self.log.error(cron)
            self.bot.log.exception(e)
        else:
            self.log.debug(cron)
        handle = self.bot.loop.call_at(
            self.loop_time + (cron.get_next() - self.time),
            self.call_cron, cron)
        self.handles[cron.uuid] = handle

    def __repr__(self):
        return '<Crons ({})>'.format(len(self))


def cron(cronline, venusian_category='irc3.plugins.cron'):
    """main decorator"""
    def wrapper(func):
        def callback(context, name, ob):
            obj = context.context
            crons = obj.get_plugin(Crons)
            if info.scope == 'class':
                callback = getattr(
                    obj.get_plugin(ob),
                    func.__name__)
            else:
                @functools.wraps(func)
                def wrapper(**kwargs):
                    return func(obj, **kwargs)
                callback = wrapper
            crons.add_cron(cronline, callback)
        info = venusian.attach(func, callback, category=venusian_category)
        return func
    return wrapper
