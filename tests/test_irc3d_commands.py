# -*- coding: utf-8 -*-
from irc3 import testing


class TestCommands(testing.ServerTestCase):

    def test_not_registered(self):
        s = self.callFTU(clients=3, opers={'superman': 'passwd'})
        del s.client1.data['nick']
        s.client1.dispatch('OPER superman passwd')
        self.assertSent(
            s.client1, ':irc.com 451 None :You have not registered')

    def test_help(self):
        s = self.callFTU(clients=1)
        p = s.get_plugin('irc3d.plugins.command.ServerCommands')
        s.client1.dispatch('HELP')
        self.assertSent(
            s.client1,
            'irc.com 704 client1 index :Help topics available to users:')
        self.assertSent(
            s.client1, 'irc.com 706 client1 index :End of /HELP')
        sent = ''.join(s.client1.sent)
        for cmd in p.keys():
            self.assertIn(cmd, sent)

    def test_help_cmd(self):
        s = self.callFTU(clients=1)
        s.client1.dispatch('HELP join')
        self.assertSent(
            s.client1, 'irc.com 704 client1 join :JOIN <channel>')
        self.assertSent(
            s.client1, 'irc.com 706 client1 join :End of /HELP')

    def test_oper(self):
        s = self.callFTU(clients=3, opers={'superman': 'passwd'})
        s.client2.modes.add('w')
        s.client1.dispatch('OPER c c')
        self.assertSent(s.client1, ':irc.com 464 client1 :Password incorrect')

        s.client1.dispatch('WALLOPS Hi!')
        self.assertSent(
            s.client1,
            (':irc.com 481 client1 '
             ':Permission Denied- You\'re not an IRC operator'))

        s.client1.dispatch('OPER superman passwd')
        self.assertSent(
            s.client1, ':irc.com 381 client1 :You are now an IRC operator')

        s.client1.dispatch('WALLOPS Hi!')
        self.assertSent(
            s.client2, ':client1!uclient1@127.0.0.1 NOTICE client2 :Hi!')
        self.assertNotSent(
            s.client3, ':client1!uclient1@127.0.0.1 NOTICE client3 :Hi!')
