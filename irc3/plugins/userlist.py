# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__doc__ = '''
==============================================
:mod:`irc3.plugins.userlist` User list plugin
==============================================

This plugin maintain a known user list and a channel list.

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

    >>> bot.test(':gawel!user@host MODE #chan +o gawel')

    >>> print(list(bot.channels['#chan'].modes['@'])[0])
    gawel

Api
===

.. autoclass:: Channel

'''
from irc3 import plugin
from irc3 import utils
from irc3 import event
from irc3 import rfc
from irc3.utils import IrcString
from collections import defaultdict


class Channel(set):
    """A set like object which contains nicknames that are on the channel and
    user modes:

    .. code-block:: python

        >>> channel = Channel()
        >>> channel.add('gawel', modes='@')
        >>> 'gawel' in channel
        True
        >>> 'gawel' in channel.modes['@']
        True
        >>> channel.remove('gawel')
        >>> 'gawel' in channel
        False
        >>> 'gawel' in channel.modes['@']
        False
    """

    def __init__(self):
        set.__init__(self)
        self.modes = defaultdict(set)

    def add(self, item, modes=''):
        set.add(self, item)
        for mode in modes:
            self.modes[mode].add(item)

    def remove(self, item):
        set.remove(self, item)
        for items in self.modes.values():
            if item in items:
                items.remove(item)

    def __repr__(self):
        return sorted(list(self))


@plugin
class Userlist(object):

    def __init__(self, bot):
        self.bot = bot
        self.connection_lost()

    def connection_lost(self):
        self.channels = defaultdict(Channel)
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
            channel = self.channels[channel]
            channel.remove(nick)
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
                for nicknames in channel.modes.values():
                    if nick in nicknames:
                        nicknames.add(new_nick)
                channel.remove(nick)
                channel.add(new_nick)

    @event('^:\S+ 353 [^&#]+(?P<channel>\S+) :(?P<nicknames>.*)')
    def names(self, channel=None, nicknames=None):
        """Initialise channel list and channel.modes"""
        statusmsg = self.bot.server_config['STATUSMSG']
        nicknames = nicknames.split(' ')
        channel = self.channels[channel]
        for item in nicknames:
            nick = item.strip(statusmsg)
            channel.add(nick, modes=item[:-len(nick)])
            self.nicks[nick] = nick

    @event(rfc.RPL_WHOREPLY)
    def who(self, channel=None, nick=None, user=None, host=None, **kw):
        """Set nick mask"""
        self.channels[channel].add(nick)
        mask = IrcString(nick + '!' + user + '@' + host)
        self.nicks[nick] = mask

    @event(rfc.MODE)
    def mode(self, target=None, modes=None, data=None, **kw):
        """Add nicknames to channel.modes"""
        if target[0] not in self.bot.server_config['CHANTYPES'] or not data:
            # not a channel or no user target
            return
        noargs = self.bot.server_config['CHANMODES'].split(',')[-1]
        data = [d for d in data.split(' ') if d]
        modes = utils.parse_modes(modes, data, noargs)
        prefix = self.bot.server_config['PREFIX']
        prefix = dict(zip(*prefix.strip('(').split(')')))
        channel = self.channels[target]
        for char, mode, target in modes:
            if mode in prefix:
                nicknames = channel.modes[prefix[mode]]
                if char == '+':
                    nicknames.add(target)
                elif target in nicknames:
                    nicknames.remove(target)
