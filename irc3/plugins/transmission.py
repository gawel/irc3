# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__doc__ = '''
===================================================
:mod:`irc3.plugins.tranmission` Transmission plugin
===================================================

Notify a channel when a torrent is done downloading

Add a ``torrent`` command to list downloading file and add new url/magnet

..
    >>> from testing import IrcBot
    >>> from testing import patch
    >>> patcher = patch('transmissionrpc.client.Client')
    >>> patched = patcher.start()

Usage::

    >>> bot = IrcBot(includes=['irc3.plugins.transmission'],
    ...              transmission=dict(channel='#mychan', host='', port='',
    ...                                user='', password=''))

..
    >>> patcher.stop()
'''
import irc3
import logging
from irc3.compat import text_type
from irc3.plugins.command import command


class Torrent(object):
    """Small wrapper to get a clean str()"""

    def __init__(self, t):
        self.t = t

    def __getattr__(self, attr):
        return getattr(self.t, attr)

    def __str__(self):
        name = self.t.name
        if not isinstance(name, text_type):
            name = name.decode('utf8', 'replace')
        return name


@irc3.plugin
class Transmission(object):

    requires = ['irc3.plugins.command', 'irc3.plugins.cron']

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config.get('transmission', {})
        self.kwargs = {}
        for k in ('address', 'port', 'user', 'password'):
            if k in self.config:
                self.kwargs[k] = self.config[k]
        self.torrents = []
        self.log = logging.getLogger(__name__)
        self.irc = logging.getLogger('irc.transmission')
        self.irc.set_irc_targets(bot, self.config['channel'])
        self.bot.add_cron('*/1 * * * *', self.check)

    @property
    def rpc(self):
        client = irc3.utils.maybedotted('transmissionrpc.Client')
        return client(**self.kwargs)

    def check(self):
        olds = [Torrent(t) for t in self.torrents]
        olds = dict([(t.id, t) for t in olds])
        self.torrents = self.rpc.get_torrents()
        for torrent in self.torrents:
            if torrent.id in olds:
                old = olds.get(torrent.id)
                if torrent.progress == 100. and old.progress != 100.:
                    torrent = Torrent(torrent)
                    self.irc.info('%s completed.', torrent)
                    yield torrent
            elif torrent.progress == 100.:
                torrent = Torrent(torrent)
                self.irc.info('%s completed.', torrent)
                yield torrent

    def filter(self, **kwargs):
        for t in self.rpc.get_torrents():
            match = True
            for k, v in kwargs.items():
                if not isinstance(v, tuple):
                    v = (v,)
                if getattr(t, k, None) not in v:
                    match = False
            if match:
                yield Torrent(t)

    @command(permission='transmission')
    def torrent(self, mask, target, args):
        """Transmission control

            %%torrent (add|list) [<url_or_magnet>]
        """
        if args['add']:
            try:
                torrent = self.rpc.add_torrent(args['<url_or_magnet>'])
            except Exception as e:
                self.log.exception(e)
                yield 'Sorry. An error occured. ({})'.format(repr(e))
            else:
                yield '{0} added.'.format(Torrent(torrent))
        elif args['list']:
            for torrent in self.filter(status='downloading'):
                yield '{0.id} - {0} - {0.progress:.2f}%'.format(torrent)
