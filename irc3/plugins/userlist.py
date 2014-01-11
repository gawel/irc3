# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__doc__ = '''
==============================================
:mod:`irc3.plugins.userlist` User list plugin
==============================================

This plugin maintain a know user list and a channel list.

..
    >>> from testing import IrcBot

Usage::

    >>> bot = IrcBot()
    >>> bot.include('irc3.plugins.userlist')
    >>> bot.test(':gawel!user@host JOIN #chan')

    >>> list(bot.channels['#chan'])
    ['gawel']
    >>> bot.nicks
    {'gawel': 'gawel!user@host'}

'''
from irc3 import plugin
from irc3 import event
from irc3 import rfc
from irc3.utils import IrcString
from collections import defaultdict


@plugin
class Userlist(object):

    def __init__(self, bot):
        self.bot = bot
        self.connection_lost()

    def connection_lost(self):
        self.channels = defaultdict(set)
        self.bot.channels = self.channels
        self.nicks = {}
        self.bot.nicks = self.nicks

    @event(rfc.JOIN_PART_QUIT)
    def join_part_quit(self, mask, event, channel=None, **kw):
        getattr(self, event.lower())(mask.lnick, mask, channel)

    def join(self, nick, mask, channel):
        if nick != self.bot.nick.lower():
            self.channels[channel].add(mask.nick)
            self.nicks[mask.nick] = mask

    def part(self, nick, mask, channel):
        if nick == self.bot.nick.lower():
            del self.channels[channel]
        else:
            self.channels[channel].remove(nick)
            if True not in [nick in c for c in self.channels.values()]:
                del self.nicks[nick]

    def quit(self, nick, mask, channel):
        if nick == self.bot.nick.lower():
            self.connection_lost()
        else:
            for channel in self.channels.values():
                if nick in channel:
                    channel.remove(nick)
            del self.nicks[nick]

    @event('^:\S+ 353 [^&#]+(?P<channel>\S+) :(?P<nicknames>.*)')
    def names(self, channel=None, nicknames=None):
        nicknames = nicknames.split(' ')
        for nick in nicknames:
            nick = nick.strip('+%@')
            lnick = nick.lower()
            self.channels[channel].add(lnick)
            self.nicks[lnick] = nick

    @event(rfc.RPL_WHOREPLY)
    def who(self, channel=None, nick=None, user=None, host=None, **kw):
        self.channels[channel].add(nick.lower())
        mask = IrcString(nick + '!' + user + '@' + host)
        self.nicks[nick.lower()] = mask
