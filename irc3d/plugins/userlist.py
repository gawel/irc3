# -*- coding: utf-8 -*-
from irc3.plugins import userlist
from irc3 import utils
from irc3 import rfc
import irc3d
import string
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

    def get_client(self, nick_or_client):
        if isinstance(nick_or_client, irc3d.IrcClient):
            return nick_or_client
        return self.nicks.get(nick_or_client)

    @irc3d.extend
    def broadcast(self, client=None, clients=None, **kwargs):
        if clients is None:
            clients = self.context.clients.values()
        else:
            clients = [self.get_client(c) for c in clients]
        for c in clients:
            c.write(kwargs['broadcast'])

    @irc3d.command
    def ISON(self, client, args=None, **kwargs):
        """ISON will return a list of users who are present on the network from
        the list that was passed in.
        This command is rarely used directly.

            %%ISON <nicks>...
        """
        nicks = [n for n in args['<nicks>'] or [] if n in self.nicks]
        client.fwrite(rfc.RPL_ISON, nicknames=' '.join(nicks))

    @irc3d.command
    def JOIN(self, client, args=None, **kwargs):
        """ The JOIN command allows you to enter a public chat area known as a
        channel. Network wide channels are proceeded by a '#', while a local
        server channel is proceeded by an '&'. More than one channel may be
        specified, separated with commas (no spaces).

        If the channel has a key set, the 2nd argument must be given to enter.
        This allows channels to be password protected.

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
        """ PART requires at least a channel argument to be given. It will exit
        the client from the specified channel. More than one channel may be
        specified, separated with commas (no spaces).

        An optional part message may be given to be displayed to the channel.

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
        """QUIT sends a message to the IRC server letting it know you would
        like to disconnect.  The quit message will be displayed to the users in
        the channels you were in when you are disconnected.

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
        """The KICK command will remove the specified user from the specified
        channel, using the optional kick message.  You must be a channel
        operator to use this command.

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

    @irc3d.command(permission=None)
    def NICK(self, client, args=None, **kwargs):
        """When first connected to the IRC server, NICK is required to set the
        client's nickname.

        NICK will also change the client's nickname once a connection has been
        established.

            %%NICK <nick>
        """
        new_nick = args['<nick>']
        if new_nick in self.nicks:
            client.fwrite(rfc.ERR_NICKNAMEINUSE, nick=new_nick)
            return

        self.nicks[new_nick] = client
        if client.registered:
            nick = client.nick
            kwargs['broadcast'] = ':{mask} NICK {new_nick}'.format(
                new_nick=new_nick, **client.data)
            client.nick = new_nick
            super(ServerUserlist, self).new_nick(
                nick, new_nick, client=client, **kwargs)
        else:  # pragma: no cover
            self.context.register(client, nick=new_nick)

    @irc3d.command
    def PRIVMSG(self, client=None, args=None, event='PRIVMSG', **kwargs):
        """ PRIVMSG will send a standard message to the user or channel
        specified.

        PRIVMSG supports the following prefixes for sending messages to
        specific clients in a channel:

        @ - channel operators only
        + - channel operators and voiced users

        The nick can be extended to fit into the following syntax:

        username@servername

        This syntax is used to securely send a message to a service or a bot.

            %%PRIVMSG <target> <:message>...
        """
        dest = args['<target>']
        target = self.nicks.get(dest, None)
        if target is not None:
            clients = [target]
        else:
            clients = self.channels.get(dest, set())
            # do not send to sender
            clients = clients.difference({client.nick})
        if clients:
            data = ' '.join(args['<:message>'])
            if not data.startswith(':'):
                data = ':' + data
            self.broadcast(
                client=client,
                broadcast=':{c.mask} {event} {<target>} {data}'.format(
                    c=client, target=target, event=event, data=data, **args),
                clients=clients)
        elif dest not in self.channels:
            client.fwrite(rfc.ERR_NOSUCHNICK, nick=dest)

    @irc3d.command
    def NOTICE(self, client=None, args=None, event='PRIVMSG', **kwargs):
        """NOTICE will send a notice message to the user or channel specified.

        NOTICE supports the following prefixes for sending messages to specific
        clients in a channel:

        @ - channel operators only
        + - channel operators and voiced users

        The nick can be extended to fit into the following syntax:

        username@servername

        This syntax is used to securely send a notice to a service or a bot.

            %%NOTICE <target> <:message>...
        """
        self.PRIVMSG(client, args, event='NOTICE', **kwargs)

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
                        elif mode in client.modes:
                            client.modes.remove(mode)
                else:
                    client.fwrite(rfc.ERR_UMODEUNKNOWNFLAG)
        else:
            client.fwrite(rfc.ERR_NOSUCHCHANNEL, channel=target)

    @irc3d.extend
    def UMODE_i(self, client, target, char, mode):
        return client.nick == target

    @irc3d.extend
    def UMODE_w(self, client, target, char, mode):
        return client.nick == target

    @irc3d.command
    def NAMES(self, client=None, args=None, **kwargs):
        """ With no channel argument, NAMES shows the names (nicks) of all
        clients logged in to the network that do not have +i flag.

        With the #channel argument, it displays the nicks on that channel, also
        respecting the +i flag of each client. If the channel specified is a
        channel that the issuing client is currently in, all nicks are listed
        in similar fashion to when the user first joins a channel.

            %%NAMES <channel>
        """
        if args:
            kwargs['channel'] = args['<channel>']
        channel = self.context.channels[kwargs['channel']]
        if self.context.config.testing:
            # easyer to test
            channel = sorted(channel)
        # everything is a public channel
        kwargs['m'] = '='
        client.fwrite((rfc.RPL_NAMREPLY, rfc.RPL_ENDOFNAMES),
                      nicknames=' '.join(channel), **kwargs)

    @irc3d.command
    def WHOIS(self, client=None, args=None, **kwargs):
        """WHOIS will display detailed user information for the specified nick.
        If the first parameter is specified, WHOIS will display information
        from the specified server, or the server that the user is on.  This is
        how to remotely see idle time and away status.

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
            if 'away_message' in target.data:
                rpl.append(rfc.RPL_AWAY)
            if channels:
                rpl.append(rfc.RPL_WHOISCHANNELS)
        rpl.append(rfc.RPL_ENDOFWHOIS)
        kwargs['m'] = '*'
        client.fwrite(rpl, channels=channels, **kwargs)
