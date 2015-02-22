# -*- coding: utf-8 -*-
import venusian
import logging
import irc3
__doc__ = '''
==========================================
:mod:`irc3.plugins.cron` Cron plugin
==========================================

Introduce a ``@cron`` decorator

Install aiocron::

    $ pip install aiocron

Create a python module with some crons:

.. literalinclude:: ../../examples/mycrons.py

..
    >>> import sys
    >>> sys.path.append('examples')
    >>> from irc3.testing import IrcBot

And register it::

    >>> context = IrcBot()
    >>> context.include('mycrons')    # register your crons

'''


@irc3.plugin
class Crons(list):

    def __init__(self, context):
        self.context = context
        self.log = logging.getLogger(__name__)
        self.factory = irc3.utils.maybedotted('aiocron.Cron')
        self.debug = self.log.getEffectiveLevel() == logging.DEBUG
        self.started = False

    def connection_made(self):
        if not self.started:
            self.start()

    def before_reload(self):
        self.stop()
        self[:] = []

    def after_reload(self):
        self.start()

    @irc3.extend
    def add_cron(self, cronline, callback, uuid=None):
        cron = self.factory(cronline, callback, start=False, uuid=uuid,
                            loop=self.context.loop)
        self.append(cron)
        if self.started:
            cron.start()
        return cron

    @irc3.extend
    def remove_cron(self, cron=None):
        cron.stop()
        self.remove(cron)

    def start(self):
        self.started = True
        for cron in self:
            cron.start()

    def stop(self):
        self.context.log.info('Stoping existing crons...')
        self.started = False
        for cron in self:
            cron.stop()

    def __repr__(self):
        return '<Crons ({0}) at {1}>'.format(len(self), id(self))


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
                callback = irc3.utils.wraps_with_context(func, obj)
            crons.add_cron(cronline, callback)
        info = venusian.attach(func, callback, category=venusian_category)
        return func
    return wrapper
