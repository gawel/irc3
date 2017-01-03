# -*- coding: utf-8 -*-
from irc3 import plugin
from irc3 import utils
from irc3 import rfc
from irc3.dec import event
from irc3.utils import IrcString
from collections import defaultdict
__doc__ = '''
==============================================
:mod:`irc3.plugins.userlist` User list plugin
==============================================

This plugin maintain a known user list and a channel list.

..
    >>> from irc3.testing import IrcBot

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
        self.topic = None

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
        return repr(sorted(self))


@plugin
class Userlist:

    def __init__(self, context):
        self.context = context
        self.connection_lost()

    def connection_lost(self, client=None):
        self.channels = defaultdict(Channel)
        self.context.channels = self.channels
        self.nicks = {}
        self.context.nicks = self.nicks

    def broadcast(self, *args, **kwargs):
        # only usefull for servers
        pass

    @event(rfc.JOIN_PART_QUIT)
    def on_join_part_quit(self, mask=None, event=None, **kwargs):
        getattr(self, event.lower())(mask.nick, mask, **kwargs)

    @event(rfc.KICK)
    def on_kick(self, mask=None, event=None, target=None, **kwargs):
        self.part(target.nick, mask=None, **kwargs)

    def join(self, nick, mask, client=None, **kwargs):
        channel = self.channels[kwargs['channel']]
        if nick != self.context.nick:
            channel.add(mask.nick)
            self.nicks[mask.nick] = client or mask
            if client:
                self.broadcast(client=client, clients=channel, **kwargs)

    def part(self, nick, mask=None, channel=None, client=None, **kwargs):
        if nick == self.context.nick:
            del self.channels[channel]
        else:
            channel = self.channels[channel]
            self.broadcast(client=client, clients=channel, **kwargs)
            channel.remove(nick)
            if True not in [nick in c for c in self.channels.values()]:
                del self.nicks[nick]

    def quit(self, nick, mask, channel=None, client=None, **kwargs):
        if nick == self.context.nick:
            self.connection_lost()
        else:
            clients = set()
            for channel in self.channels.values():
                if nick in channel:
                    clients.update(channel)
                    channel.remove(nick)
            self.broadcast(client=client, clients=clients, **kwargs)
            del self.nicks[nick]

    @event(rfc.NEW_NICK)
    def new_nick(self, nick=None, new_nick=None, client=None, **kwargs):
        """update list on new nick"""
        if client is None:
            self.nicks[new_nick] = new_nick + '!' + nick.host
            nick = nick.nick
        clients = set()
        for channel in self.channels.values():
            if nick in channel:
                for nicknames in channel.modes.values():
                    if nick in nicknames:
                        nicknames.add(new_nick)
                channel.remove(nick)
                clients.update(channel)
                channel.add(new_nick)
        del self.nicks[nick]
        self.broadcast(client=client, clients=clients, **kwargs)

    @event(rfc.RPL_NAMREPLY)
    def names(self, channel=None, data=None, **kwargs):
        """Initialise channel list and channel.modes"""
        statusmsg = self.context.server_config['STATUSMSG']
        nicknames = data.split(' ')
        channel = self.channels[channel]
        for item in nicknames:
            nick = item.strip(statusmsg)
            channel.add(nick, modes=item[:-len(nick)])
            self.nicks[nick] = nick

    @event(rfc.RPL_WHOREPLY)
    def who(self, channel=None, nick=None, username=None, server=None, **kw):
        """Set nick mask"""
        self.channels[channel].add(nick)
        mask = IrcString(nick + '!' + username + '@' + server)
        self.nicks[nick] = mask

    @event(rfc.MODE)
    def mode(self, target=None, modes=None, data=None, client=None, **kw):
        """Add nicknames to channel.modes"""
        if target[0] not in self.context.server_config['CHANTYPES'] \
           or not data:
            # not a channel or no user target
            return
        noargs = self.context.server_config['CHANMODES'].split(',')[-1]
        if not isinstance(data, list):
            data = [d for d in data.split(' ') if d]
        if not modes.startswith(('+', '-')):
            modes = '+' + modes
        modes = utils.parse_modes(modes, data, noargs)
        prefix = self.context.server_config['PREFIX']
        prefix = dict(zip(*prefix.strip('(').split(')')))
        channel = self.channels[target]
        for char, mode, tgt in modes:
            if mode in prefix:
                nicknames = channel.modes[prefix[mode]]
                if char == '+':
                    nicknames.add(tgt)
                elif tgt in nicknames:
                    nicknames.remove(tgt)
                if client is not None:
                    broadcast = (
                        ':{mask} MODE {target} {char}{mode} {tgt}').format(
                        char=char, mode=mode, target=target, tgt=tgt,
                        **client.data)
                    self.broadcast(client=client, broadcast=broadcast,
                                   clients=channel)

    @event(rfc.RPL_TOPIC)
    def topic(self, channel=None, data=None, client=None, **kwargs):
        self.channels[channel].topic = data
