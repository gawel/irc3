# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import time
from irc3 import rfc
from .command import command
import irc3d
__doc__ = '''
==============================================
:mod:`irc3d.plugins.core` Server core plugin
==============================================

Provide basic server functionality.

Use :mod:`~irc3.plugins.userlist` to maintain a list of channels/users

API
===

.. autoclass:: Core
   :members:

    .. autoattribute:: requires
'''


@irc3d.plugin
class Core(object):

    requires = [
        'irc3d.plugins.userlist',
        'irc3d.plugins.command',
    ]

    def __init__(self, context):
        self.context = context

    @command(permission=None)
    def USER(self, client, args=None):
        """USER

            %%USER <username> <hostname> <servername> <:realname>...
        """
        if client.registered:
            client.fwrite(rfc.ERR_ALREADYREGISTRED)
        else:
            self.register(client,
                          username=args['<username>'],
                          realname=' '.join(args['<:realname>']).lstrip(':'))

    @irc3d.extend
    def register(self, client, **kwargs):
        data = client.data
        data.update(kwargs)
        if client.registered:
            if 'signon' not in data:
                data['signon'] = int(time.time())
                client.nick = data['nick']
                self.context.notify('connection_made', client=client)
                client.fwrite(':{c.srv} 001 {c.nick} :Welcome')
                self.VERSION(client)
                self.MOTD(client)

    @command
    def VERSION(self, client, args=None):
        """VERSION

            %%VERSION
        """
        client.fwrite(':{c.srv} 004 {c.nick} :irc3d {c.version}')

    @command
    def MOTD(self, client, args=None):
        """MOTD

            %%MOTD
        """
        config = self.context.config
        if 'motd_fmt' not in config:
            config['motd_fmt'] = rfc.ERR_NOMOTD
            if not config.testing and os.path.isfile(config.motd):
                with open(config.motd) as fd:
                    lines = [l.rstrip() for l in fd.readlines()]
                    data = [rfc.RPL_MOTDSTART] + [
                        ':{c.srv} 372 {c.nick} :' + l for l in lines
                    ] + [rfc.RPL_ENDOFMOTD]
                    config['motd_fmt'] = data

        client.fwrite(config.motd_fmt,
                      server=client.srv, version=client.version)

    @command
    def PING(self, client, args):
        """PING

            %%PING <data>
        """
        client.fwrite(':{c.srv} PONG {c.srv} :{<data>}', **args)

    @command(permission='oper')
    def DIE(self, client=None, args=None, **kwargs):
        """DIE

            %%DIE
        """
        self.context.log.warn('%r killed me', client)
        self.context.SIGINT()

    @command(permission='oper')
    def WALLOPS(self, client=None, args=None, **kwargs):
        """WALLOPS

            %%WALLOPS <message>...
        """
        kw = dict(mask=client.mask, message=' '.join(args['<message>']))
        for c in self.context.nicks.values():
            if client is not c and 'w' in c.modes:
                c.fwrite(':{mask} NOTICE {c.nick} :{message}', **kw)

    @command
    def AWAY(self, client, args):
        """AWAY

            %%AWAY [<:reason>...]
        """
        reason = ' '.join(args['<:reason>']).lstrip(':')
        if not reason:
            client.data.pop('away', None)
            client.data.pop('away_message', None)
            client.fwrite(rfc.RPL_UNAWAY)
        elif reason:
            client.data['away'] = self.context.loop.time()
            client.data['away_message'] = reason
            client.fwrite(rfc.RPL_NOWAWAY)
