# -*- coding: utf-8 -*-
__doc__ = '''
==========================================
:mod:`irc3.plugin.log` Log plugin
==========================================

Logging / debuging plugin

Usage::

    >>> from irc3 import IrcBot
    >>> bot = IrcBot()
    >>> bot.include('irc3.plugins.log')
'''
import logging
import irc3


class RawLog:

    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger('raw.' + bot.nick)

    @irc3.event(r'^:(?P<raw>.*)')
    def debug(self, raw):
        if ' 372 ' in raw or raw.startswith('PING'):
            self.log.debug(':' + raw)
        else:
            self.log.info(':' + raw)
