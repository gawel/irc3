# -*- coding: utf-8 -*-
import logging
import irc3d
import irc3
__doc__ = '''
==========================================
:mod:`irc3.plugins.log` Log plugin
==========================================

Logging / debuging plugin

..
    >>> from irc3.testing import IrcBot

Usage::

    >>> bot = IrcBot()
    >>> bot.include('irc3.plugins.log')
'''


class RawLog:

    def __init__(self, context):
        self.context = context
        name = 'raw.%s' % (context.nick or 'irc3d')
        self.log_in = logging.getLogger(name + ' <<')
        self.log_in.setLevel(logging.DEBUG)
        self.log_out = logging.getLogger(name + ' >>')
        self.log_out.setLevel(logging.DEBUG)

    @irc3d.event(r'^(?P<raw>.*)', venusian_category='irc3d.debug')
    @irc3.event(r'^(?P<raw>.*)', venusian_category='irc3.debug')
    @irc3.dcc_event(r'^(?P<raw>.*)', venusian_category='irc3.debug')
    def debug_input(self, raw=None, client=None, iotype='in', **kwargs):
        self.log(raw, client, iotype)

    @irc3d.event(r'^(?P<raw>.*)', iotype='out',
                 venusian_category='irc3d.debug')
    @irc3.event(r'^(?P<raw>.*)', iotype='out', venusian_category='irc3.debug')
    @irc3.dcc_event(r'^(?P<raw>.*)', iotype='out',
                    venusian_category='irc3.debug')
    def debug_output(self, raw=None, client=None, iotype='out', **kwargs):
        self.log(raw, client, iotype)

    def log(self, raw, client=None, iotype=None):
        if raw.strip():
            log = getattr(self, 'log_' + iotype)
            if client is not None:
                log.debug('[%-7r] %s', client, raw)
            else:
                log.debug(raw)
