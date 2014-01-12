# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from irc3.testing import BotTestCase
from irc3.testing import MagicMock
from irc3.testing import patch
from irc3.plugins.transmission import Transmission
from transmissionrpc.torrent import Torrent


class TestTransmission(BotTestCase):

    config = dict(
        nick='nono',
        includes=['irc3.plugins.transmission'],
        transmission=dict(username='user', password='secret',
                          channel='#irc3'),
    )

    def setUp(self):
        patcher = patch('transmissionrpc.client.Client.get_torrents')
        self.get_torrents = patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch('transmissionrpc.client.Client.add_torrent')
        self.add_torrent = patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch('transmissionrpc.client.Client.get_session')
        patcher.start()
        self.addCleanup(patcher.stop)

    def callTFTU(self, **kwargs):
        kwargs = dict(dict(sizeWhenDone=200, leftUntilDone=100), **kwargs)
        if 'name' not in kwargs:
            kwargs['name'] = 'awesome torrent {id}'.format(**kwargs)
        if kwargs['leftUntilDone'] != 0:
            kwargs['status'] = 4
        else:
            kwargs['status'] = 6
        cli = MagicMock()
        cli.rpc_version = 15
        return Torrent(cli, kwargs)

    def test_notification(self):
        t1 = self.callTFTU(id=1)
        self.get_torrents.return_value = [t1]
        bot = self.callFTU()
        plugin = bot.get_plugin(Transmission)
        self.assertEqual(len(list(plugin.check())), 0)
        self.assertEqual(len(plugin.torrents), 1)

        t1 = self.callTFTU(id=1, leftUntilDone=0.)
        t2 = self.callTFTU(id=2)
        self.get_torrents.return_value = [t1, t2]
        self.assertEqual(len(list(plugin.check())), 1)
        self.assertSent([
            'PRIVMSG #irc3 :INFO awesome torrent 1 completed.',
        ])

        t1 = self.callTFTU(id=1, leftUntilDone=0.)
        t2 = self.callTFTU(id=2)
        t2 = self.callTFTU(id=3, leftUntilDone=0)
        self.get_torrents.return_value = [t1, t2]
        self.assertEqual(len(list(plugin.check())), 1)

    def test_filter(self):
        bot = self.callFTU()
        t1 = self.callTFTU(id=1, leftUntilDone=0.)
        t2 = self.callTFTU(id=2)
        self.get_torrents.return_value = [t1, t2]
        plugin = bot.get_plugin(Transmission)
        self.assertEqual(len(list(plugin.filter(status='downloading'))), 1)

    def test_list(self):
        bot = self.callFTU()
        t1 = self.callTFTU(id=1, name=b'sup\xc3\xa9r', leftUntilDone=10.)
        t2 = self.callTFTU(id=2, leftUntilDone=90.)
        self.get_torrents.return_value = [t1, t2]

        bot.dispatch(':n!u@h PRIVMSG nono :!torrent list')
        self.assertSent([
            'PRIVMSG n :1 - supér - 95.00%',
            'PRIVMSG n :2 - awesome torrent 2 - 55.00%',
        ])

    def test_add(self):
        bot = self.callFTU()
        t1 = self.callTFTU(id=1, name=b'sup\xc3\xa9r', leftUntilDone=10.)
        self.add_torrent.return_value = t1
        bot.dispatch(':n!u@h PRIVMSG nono :!torrent add magnet://')
        self.assertSent([
            'PRIVMSG n :supér added.',
        ])

    def test_add_failure(self):
        bot = self.callFTU()
        bot.log.setLevel(1000)
        self.add_torrent.side_effect = KeyError(str('error'))
        bot.dispatch(':n!u@h PRIVMSG nono :!torrent add magnet://')
        self.assertSent([
            "PRIVMSG n :Sorry. An error occured. (KeyError('error',))",
        ])
