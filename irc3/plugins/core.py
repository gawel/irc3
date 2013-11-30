# -*- coding: utf-8 -*-
__doc__ = '''
==============================================
:mod:`irc3.plugin.core` Core plugin
==============================================

Core events

.. autofunction:: pong


.. autofunction:: recompile

.. autofunction:: badnick

.. autofunction:: autojoin

Usage::

    >>> from irc3 import IrcBot
    >>> bot = IrcBot()
    >>> bot.include('irc3.plugins.core')
'''
from irc3 import event
from irc3 import rfc


@event(rfc.PING)
def pong(bot, data):
    """PING reply"""
    bot.send('PONG ' + data)


@event(rfc.NEW_NICK)
def recompile(bot, nick=None, new_nick=None, **kw):
    """recompile regexp on new nick"""
    if bot.nick == nick.nick:
        bot.config['nick'] = new_nick
        bot.recompile()


@event(rfc.ERR_NICK)
def badnick(bot, me=None, nick=None, **kw):
    """Use alt nick on nick error"""
    bot.set_nick('%s_' % bot.nick)


@event(rfc.RPL_ENDOFMOTD)
def autojoin(bot, **kw):
    """autojoin at the end of MOTD"""
    bot.config['nick'] = kw['me']
    bot.recompile()
    for channel in bot.config.get('autojoins', ['#irc3']):
        bot.join(channel)
