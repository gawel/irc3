# -*- coding: utf-8 -*-
__doc__ = '''
==============================================
:mod:`irc3.plugin.userlist` User list plugin
==============================================

This plugin maintain a know user list and a channel list.

Usage::

    >>> from irc3 import IrcBot
    >>> bot = IrcBot(async=False)
    >>> bot.include('irc3.plugins.userlist')
    >>> plugin = bot.get_plugin('userlist')
    >>> plugin.connection_lost()
    >>> events = bot.dispatch(':gawel!user@host JOIN #chan')
    >>> plugin.channels.items()
    dict_items([('#chan', Channel({'gawel'}))])
    >>> plugin.nicks.items()
    dict_items([('gawel', 'gawel!user@host')])

'''
from irc3 import event
from irc3 import rfc
from irc3.utils import IrcString
from collections import defaultdict


class Channel(set):

    def __init__(self):
        self.ops = set()


class Userlist:

    def __init__(self, bot):
        self.bot = bot
        self.connection_lost()

    def connection_lost(self):
        self.channels = defaultdict(Channel)
        self.nicks = {}

    @event(rfc.JOIN_PART_QUIT)
    def join_part_quit(self, mask, event, channel=None, **kw):
        getattr(self, event.lower())(mask, channel)

    def join(self, mask, channel):
        nick = mask.lnick
        if nick == self.bot.nick.lower():
            self.bot.send('WHO ' + channel)
        else:
            self.channels[channel].add(mask.nick)
            self.nicks[mask.nick] = mask

    def part(self, mask, channel):
        nick = mask.lnick
        if nick == self.bot.nick.lower():
            del self.channels[channel]
        else:
            self.channels[channel].remove(nick)
            if not [nick in c for c in self.channels.values()]:
                del self.nicks[nick]

    def quit(self, mask, channel):
        nick = mask.lnick
        if nick == self.bot.nick.lower():
            self.connection_lost()
        else:
            for channel in self.channels.values():
                if nick in channel:
                    channel.remove(nick)
            del self.nicks[nick]

    @event(rfc.RPL_WHOREPLY)
    def who(self, channel=None, nick=None, user=None, host=None, **kw):
        self.channels[channel].add(nick.lower())
        mask = IrcString(nick + '!' + user + '@' + host)
        self.nicks[nick.lower()] = mask
