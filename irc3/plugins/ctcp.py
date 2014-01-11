# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__doc__ = '''
==============================================
:mod:`irc3.plugins.ctcp` CTCP replies
==============================================

..
    >>> from testing import IrcBot

Usage::

    >>> bot = IrcBot(ctcp=dict(foo='bar'))
    >>> bot.include('irc3.plugins.ctcp')

Try to send a ``CTCP FOO``::

    >>> bot.test(':gawel!user@host PRIVMSG irc3 :\x01FOO\x01', show=False)
    >>> # remove escape char for testing..
    >>> print(bot.sent[0].replace('\x01', '01'))
    NOTICE gawel :01FOO bar01
'''
from irc3 import event
from irc3 import rfc


@event(rfc.CTCP)
def ctcp(bot, mask=None, target=None, ctcp=None, **kw):
    """ctcp replies"""
    lctcp = ctcp.lower()
    if lctcp in bot.config.ctcp:
        data = bot.config.ctcp[lctcp].format(**bot.config)
        bot.ctcp_reply(mask.nick, '%s %s' % (ctcp, data))
