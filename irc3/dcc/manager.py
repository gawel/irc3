# -*- coding: utf-8 -*-
import os
from functools import partial
from collections import defaultdict
from irc3.compat import asyncio
from irc3.compat import PY35
from irc3.utils import slugify
from irc3.utils import maybedotted
from irc3.dcc.client import DCCChat
from irc3.dcc.client import DCCGet

if PY35:
    from irc3.dcc.client import DCCSend
else:
    try:
        from irc3.dcc.optim import DCCSend
    except ImportError:  # pragma: no cover
        from irc3.dcc.client import DCCSend

DCC_TYPES = ('chat', 'get', 'send')


class DCCManager:
    """Manage DCC connections"""

    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop
        self.config = cfg = bot.config.get('dcc', {})
        self.config.update(
            send_limit_rate=int(cfg.get('send_limit_rate', 0)),
            send_block_size=int(cfg.get('send_block_size', DCCSend.block_size))
        )
        self.connections = {}
        self.protocols = {}
        for klass in (DCCChat, DCCGet, DCCSend):
            n = klass.type
            self.config.update({
                n + '_limit': int(cfg.get(n + '_limit', 100)),
                n + '_user_limit': int(cfg.get(n + '_user_limit', 1)),
                n + '_accept_timeout': int(cfg.get(n + '_accept_timeout', 60)),
                n + '_idle_timeout': int(cfg.get(n + '_idle_timeout', 60 * 5)),
            })
            klass = maybedotted(self.config.get(n + '_protocol', klass))
            self.connections[n] = {'total': 0, 'masks': defaultdict(dict)}
            self.protocols[n] = klass
        self.seeks = {}

    def created(self, protocol, future):
        if protocol.port is None:
            server = future.result()
            protocol.port = server.sockets[0].getsockname()[1]
            protocol.idle_handle = self.loop.call_later(
                self.config[protocol.type + '_accept_timeout'],
                server.close)
            ctcp_msg = protocol.ctcp.format(protocol)
            self.bot.ctcp(protocol.mask.nick, ctcp_msg)
        else:
            transport, protocol = future.result()
            protocol.idle_handle = self.loop.call_later(
                self.config[protocol.type + '_accept_timeout'],
                protocol.close)
        info = self.connections[protocol.type]
        info['total'] += 1
        info['masks'][protocol.mask][protocol.port] = protocol
        protocol.ready.set_result(protocol)

    def create(self, name_or_class, mask, filepath=None, **kwargs):
        """Create a new DCC connection. Return an ``asyncio.Protocol``"""
        if isinstance(name_or_class, type):
            name = name_or_class.type
            protocol = name_or_class
        else:
            name = name_or_class
            protocol = self.protocols[name]
        assert name in DCC_TYPES
        if filepath:
            kwargs.setdefault('limit_rate',
                              self.config['send_limit_rate'])
            kwargs['filepath'] = filepath
            if protocol.type == DCCSend.type:
                kwargs.setdefault('offset', 0)
                kwargs.update(
                    filename_safe=slugify(os.path.basename(filepath)),
                    filesize=os.path.getsize(filepath),
                )
            elif protocol.type == DCCGet.type:
                try:
                    offset = os.path.getsize(filepath)
                except OSError:
                    offset = 0
                kwargs.setdefault('offset', offset)
                kwargs.setdefault('resume', False)
        kwargs.setdefault('port', None)
        f = protocol(
            mask=mask, ip=int(self.bot.ip),
            bot=self.bot, loop=self.loop, **kwargs)

        if kwargs['port']:
            task = asyncio.async(
                self.loop.create_connection(f.factory, f.host, f.port),
                loop=self.loop)
            task.add_done_callback(partial(self.created, f))
        else:
            task = asyncio.async(
                self.loop.create_server(
                    f.factory, '0.0.0.0', 0, backlog=1),
                loop=self.loop)
            task.add_done_callback(partial(self.created, f))
        return f

    def resume(self, mask, filename, port, pos):
        """Resume a DCC send"""
        self.connections['send']['masks'][mask][port].offset = pos
        message = 'DCC ACCEPT %s %d %d' % (filename, port, pos)
        self.bot.ctcp(mask, message)

    def is_allowed(self, name_or_class, mask):  # pragma: no cover
        """Return True is a new connection is allowed"""
        if isinstance(name_or_class, type):
            name = name_or_class.type
        else:
            name = name_or_class
        info = self.connections[name]
        limit = self.config[name + '_limit']
        if limit and info['total'] >= limit:
            msg = (
                "Sorry, there is too much DCC %s active. Please try again "
                "later.") % name.upper()
            self.bot.notice(mask, msg)
            return False
        if mask not in info['masks']:
            return True
        limit = self.config[name + '_user_limit']
        if limit and info['masks'][mask] >= limit:
            msg = (
                "Sorry, you have too many DCC %s active. Close the other "
                "connection(s) or wait a few seconds and try again."
            ) % name.upper()
            self.bot.notice(mask, msg)
            return False
        return True
