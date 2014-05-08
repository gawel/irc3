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

    >>> print(list(bot.channels['#chan'])[0])
    gawel
    >>> print(list(bot.nicks.keys())[0])
    gawel

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
    def on_join_part_quit(self, mask, event, channel=None, **kw):
        getattr(self, event.lower())(mask.nick, mask, channel)

    @event(rfc.KICK)
    def on_kick(self, mask, event, channel=None, target=None, **kw):
        self.part(target.nick, None, channel)

    def join(self, nick, mask, channel):
        if nick != self.bot.nick:
            self.channels[channel].add(mask.nick)
            self.nicks[mask.nick] = mask

    def part(self, nick, mask, channel):
        if nick == self.bot.nick:
            del self.channels[channel]
        else:
            self.channels[channel].remove(nick)
            if True not in [nick in c for c in self.channels.values()]:
                del self.nicks[nick]

    def quit(self, nick, mask, channel):
        if nick == self.bot.nick:
            self.connection_lost()
        else:
            for channel in self.channels.values():
                if nick in channel:
                    channel.remove(nick)
            del self.nicks[nick]

    @event(rfc.NEW_NICK)
    def new_nick(self, nick=None, new_nick=None, **kw):
        """update list on new nick"""
        self.nicks[new_nick] = new_nick + '!' + nick.host
        nick = nick.nick
        for channel in self.channels.values():
            if nick in channel:
                channel.remove(nick)
                channel.add(new_nick)

    @event('^:\S+ 353 [^&#]+(?P<channel>\S+) :(?P<nicknames>.*)')
    def names(self, channel=None, nicknames=None):
        nicknames = nicknames.split(' ')
        for nick in nicknames:
            nick = nick.strip('+%@')
            self.channels[channel].add(nick)
            self.nicks[nick] = nick

    @event(rfc.RPL_WHOREPLY)
    def who(self, channel=None, nick=None, user=None, host=None, **kw):
        self.channels[channel].add(nick)
        mask = IrcString(nick + '!' + user + '@' + host)
        self.nicks[nick] = mask
