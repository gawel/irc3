# -*- coding: utf-8 -*-
from irc3.plugins import userlist
from irc3 import rfc
import irc3d


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
            clients = [self.nicks.get(nick) for nick in clients]
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

    @irc3d.event(rfc.MODE)
    def mode(self, **kw):
        """MODE

            %%MODE <channel> <modes> <nicks>...
        """
        super(ServerUserlist, self).mode(**kw)
