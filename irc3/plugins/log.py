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


@irc3.plugin
class RawLog:

    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger('raw.' + bot.nick)
        self.log.setLevel(logging.DEBUG)

    @irc3.event(r'^(?P<raw>.*)', venusian_category='irc3.debug')
    def debug(self, raw):
        if not (' 372 ' in raw or ' 00' in raw or raw.startswith('PING')):
            if raw.strip():
                self.log.debug(raw)
