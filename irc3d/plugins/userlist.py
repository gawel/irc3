# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__doc__ = '''
============================================================
:mod:`irc3d.plugins.userlist` Nick and channel related stuff
============================================================

Use :mod:`~irc3.plugins.userlist` to maintain a list of channels/users

API
===

.. autoclass:: ServerUserlist
   :members:

'''
from irc3.plugins import userlist
from irc3 import utils
from irc3 import rfc
import irc3d
import string


@irc3d.plugin
class ServerUserlist(userlist.Userlist):

    def connection_made(self, client=None):
        self.nicks[client.data['nick']] = client

    def connection_lost(self, client=None):
        if client is None:
            super(ServerUserlist, self).connection_lost()
        else:
            if self.nicks.get(client.nick):
                self.QUIT(client,
                          {'<:reason>': 'Connection reset by peer'})

    @irc3d.extend
    def broadcast(self, client=None, clients=None, **kwargs):
        if clients is None:
            clients = self.context.clients.values()
        else:
            clients = [self.nicks.get(str(c)) for c in clients]
        for c in clients:
            c.write(kwargs['broadcast'])

    @irc3d.command
    def JOIN(self, client, args=None, **kwargs):
        """JOIN

            %%JOIN <channel>
        """
        message = ':{mask} JOIN {<channel>}'
        kwargs.update(
            broadcast=message.format(mask=client.mask, **args),
            channel=args['<channel>'])
        self.join(client.nick, client.mask, client=client, **kwargs)
        client.channels.add(args['<channel>'])
        self.NAMES(client=client, **kwargs)

    @irc3d.command
    def PART(self, client, args=None, **kwargs):
        """PART

            %%PART <channel> [<:reason>...]
        """
        message = ':{mask} PART {<channel>}'
        if args.get('<:reason>'):
            args['data'] = ' '.join(args['<:reason>'])
            message += ' {data}'
        kwargs.update(
            broadcast=message.format(mask=client.mask, **args),
            channel=args.get('<channel>'),
        )
        self.part(client.nick, client.mask, **kwargs)
        client.channels.remove(args['<channel>'])

    @irc3d.command
    def QUIT(self, client, args=None, **kwargs):
        """QUIT

            %%QUIT [<:reason>...]
        """
        message = ':{mask} QUIT'
        if args.get('<:reason>'):
            args['data'] = ' '.join(args['<:reason>'])
            message += ' {data}'
        kwargs.update(
            broadcast=message.format(mask=client.mask, **args),
        )
        self.quit(client.nick, client.mask, **kwargs)
        client.close()

    @irc3d.command
    def KICK(self, client, args=None, **kwargs):
        """KICK

            %%KICK <channel> <target> [<:reason>...]
        """
        message = ':{mask} KICK {<channel>}'
        if args.get('<:reason>'):
            args['data'] = ' '.join(args['<:reason>'])
            message += ' {data}'
        kwargs.update(
            broadcast=message.format(mask=client.mask, **args),
            channel=args.get('<channel>'),
        )
        self.part(args['<target>'], client.mask, **kwargs)

    @irc3d.command
    def NICK(self, client, args=None, **kwargs):
        """NICK

            %%NICK <nick>
        """
        new_nick = args['<nick>']
        self.nicks[new_nick] = client
        if client.registered:
            nick = client.nick
            kwargs['broadcast'] = ':{mask} NICK {new_nick}'.format(
                new_nick=new_nick, **client.data)
            client.nick = new_nick
            super(ServerUserlist, self).new_nick(
                nick, new_nick, client=client, **kwargs)
        else:
            self.context.register(client, nick=new_nick)

    @irc3d.command
    def PRIVMSG(self, client=None, args=None, event='PRIVMSG', **kwargs):
        """PRIVMSG

            %%PRIVMSG <target> <:message>...
        """
        target = self.nicks.get(args['<target>'], None)
        if target is not None:
            clients = [target]
        else:
            clients = self.channels.get(args['<target>'], None)
        if clients is not None:
            data = ' '.join(args['<:message>'])
            self.broadcast(
                client=client,
                broadcast=':{c.mask} {event} {<target>} {data}'.format(
                    c=client, target=target, event=event, data=data, **args),
                clients=clients)
        else:
            client.fwrite(rfc.ERR_NOSUCHNICK)

    @irc3d.event(rfc.MODE)
    def mode(self, target=None, **kw):
        """MODE

            %%MODE <channel> <modes> <nicks>...
            %%MODE <modes> <nick>
        """
        if target.is_channel:
            super(ServerUserlist, self).mode(target=target, **kw)
        elif kw['data'] is None:
            client = kw['client']
            modes = kw['modes']
            if not modes.startswith(('+', '-')):
                modes = '+' + modes
            modes = utils.parse_modes(modes, noargs=string.ascii_letters)
            for char, mode, tgt in modes:
                meth = getattr(self.context, 'UMODE_' + mode, None)
                if meth is not None:
                    if meth(client, target, char, mode):
                        if char == '+':
                            client.modes.add(mode)
                        elif char in client.modes:
                            client.modes.remove(mode)
                else:
                    client.fwrite(rfc.ERR_UMODEUNKNOWNFLAG)
        else:
            client.fwrite(rfc.ERR_NOSUCHCHANNEL, channel=target)

    @irc3d.extend
    def UMODE_i(self, client, target, char, mode):
        return client.nick == target

    @irc3d.command
    def NAMES(self, client=None, args=None, **kwargs):
        """NAMES

            %%NAMES <channel>
        """
        if args:
            kwargs['channel'] = args['<channel>']
        channel = self.context.channels[kwargs['channel']]
        client.fwrite((rfc.RPL_NAMREPLY, rfc.RPL_ENDOFNAMES),
                      nicknames=' '.join(channel), **kwargs)

    @irc3d.command
    def WHOIS(self, client=None, args=None, **kwargs):
        """WHOIS

            %%WHOIS <nick>
        """
        try:
            target = self.nicks[args['<nick>']]
            kwargs.update(target.data)
        except:
            channels = None
            kwargs['nick'] = args['<nick>']
            rpl = [rfc.ERR_NOSUCHNICK]
        else:
            channels = ' '.join(target.channels)
            rpl = [rfc.RPL_WHOISUSER]
            if channels:
                rpl.append(rfc.RPL_WHOISCHANNELS)
        rpl.append(rfc.RPL_ENDOFWHOIS)
        client.fwrite(rpl, channels=channels, **kwargs)
