# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from irc3.compat import Queue
from irc3.compat import QueueFull
import irc3
__doc__ = '''
==============================================
:mod:`irc3.plugins.ctcp` CTCP replies
==============================================

..
    >>> from irc3.testing import IrcBot
    >>> from irc3.testing import ini2config

Usage::

    >>> config = ini2config("""
    ... [bot]
    ... includes =
    ...     irc3.plugins.ctcp
    ... [ctcp]
    ... foo = bar
    ... """)
    >>> bot = IrcBot(**config)

Try to send a ``CTCP FOO``::

    >>> bot.test(':gawel!user@host PRIVMSG irc3 :\x01FOO\x01', show=False)
    >>> # remove escape char for testing..
    >>> print(bot.sent[0].replace('\x01', '01'))
    NOTICE gawel :01FOO bar01
'''


@irc3.plugin
class CTCP(object):
    """ctcp replies"""

    def __init__(self, bot):
        maxsize = int(bot.config.get('ctcp_max_replies', 3))
        self.queue = Queue(loop=bot.loop, maxsize=maxsize)
        self.handle = None
        self.event = irc3.event(irc3.rfc.CTCP, self.on_ctcp)
        bot.attach_events(self.event)
        self.bot = bot

    def clear_queue(self):
        self.bot.log.info('CTCP clear queue')
        while not self.queue.empty():
            self.queue.get_nowait()
        self.handle = None

    def handle_flood(self):
        self.bot.log.warn('CTCP Flood detected. '
                          'Ignoring requests for 30s')
        # ignore events for 30s
        self.bot.detach_events(self.event)
        self.bot.loop.call_later(30, self.bot.attach_events, self.event)

    def on_ctcp(self, mask=None, target=None, ctcp=None, **kw):
        lctcp = ctcp.split(' ')[0].lower()
        if lctcp in self.bot.config.ctcp:
            try:
                self.queue.put_nowait((mask.nick, lctcp))
            except QueueFull:
                self.handle_flood()
            else:
                if self.handle is None:
                    self.handle = self.bot.loop.call_later(1, self.clear_queue)
                data = self.bot.config.ctcp[lctcp].format(now=datetime.now(),
                                                          **self.bot.config)
                self.bot.ctcp_reply(mask.nick, '%s %s' % (lctcp.upper(), data))
