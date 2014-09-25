# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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
        if client.registered:
            client.fwrite(rfc.ERR_ALREADYREGISTRED)
        else:
            self.register(client, **kwargs)

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
                client.fwrite(':{c.srv} 004 {c.nick} :irc3d {c.version}')
                self.MOTD(client)

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
                    config['motd_fmt'] = '\r\n'.join(data)

        client.fwrite(config.motd_fmt, server=client.srv)

    @command
    def PING(self, client, args):
        """PING

            %%PING <data>
        """
        client.fwrite(':{c.srv} PONG {c.srv} :{<data>}', **args)
