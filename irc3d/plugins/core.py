# -*- coding: utf-8 -*-
__doc__ = '''
==============================================
:mod:`irc3.plugins.server` Server core plugin
==============================================

Provide basic server functionality.

Use :mod:`~irc3.plugins.userlist` to maintain a list of channels/users

API
===

.. autoclass:: Core
   :members:

    .. autoattribute:: requires
'''
import os
import time
from irc3 import rfc
from .command import command
import irc3d


@irc3d.plugin
class Core(object):

    requires = [
        'irc3d.plugins.userlist',
        'irc3d.plugins.command',
    ]

    def __init__(self, context):
        self.context = context

    @irc3d.event((
        'USER (?P<username>\S+) (?P<hostname>\S+) '
        '(?P<servername>\S+) :(?P<realname>.*)'))
    def user(self, client=None, **kwargs):
        """User connection"""
        self.register(client, **kwargs)

    @irc3d.extend
    def register(self, client, **kwargs):
        data = client.data
        data.update(kwargs)
        if client.registered:
            if 'register_time' not in data:
                data['register_time'] = time.time()
                client.nick = data['nick']
                self.context.notify('connection_made', client=client)
                client.fwrite(':{servername} 001 {nick} :Welcome')
                client.fwrite(':{servername} 004 {nick} :irc3d {version}')
                self.MOTD(client)

    @command
    def MOTD(self, client, args=None):
        """MOTD

            %%MOTD
        """
        config = self.context.config
        if 'motd_fmt' not in config:
            config['motd_fmt'] = (
                ':{servername} 422 {nick} :MOTD File is missing')
            if not config.testing and os.path.isfile(config.motd):
                with open(config.motd) as fd:
                    lines = [l.rstrip() for l in fd.readlines()]
                    data = [(
                        ':{servername} 375 {nick} :'
                        '- {servername} Message of the day -'
                    )] + [
                        ':{servername} 372 {nick} :' + l for l in lines
                    ] + [':{servername} 376 {nick} :End of /MOTD command']
                    config['motd_fmt'] = '\r\n'.join(data)

        client.fwrite(config.motd_fmt)

    @irc3d.extend
    @command
    def NAMES(self, client=None, args=None, **kwargs):
        """NAMES

            %%NAMES <channel>
        """
        if args:
            kwargs['channel'] = args['<channel>']
        channel = self.context.channels[kwargs['channel']]
        client.fwrite((
            ':{servername} 353 {nick} @ {channel} :{nicknames}\r\n'
            ':{servername} 366 {nick} {channel} :End of /NAMES list'),
            nicknames=' '.join(channel), **kwargs)

    @command
    def PING(self, client, args):
        """PING

            %%PING <data>
        """
        client.fwrite(':{servername} PONG {servername} :{<data>}', **args)

    @irc3d.event(rfc.PRIVMSG)
    def privmsg(self, client=None, target=None, **kwargs):
        """PRIVMSG/NOTICE"""
        if target.is_channel:
            clients = self.context.channels[target]
        else:
            clients = [target]
        self.context.broadcast(
            client=client,
            broadcast=':{mask} {event} {target} :{data}'.format(
                mask=client.mask, target=target, **kwargs),
            clients=clients)
