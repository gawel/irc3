# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase


class TestSasl(BotTestCase):

    def test_sasl_plain(self):
        bot = self.callFTU(sasl_username='foo', sasl_password='bar')
        bot.notify('connection_ready')
        bot.dispatch(':s CAP * LS :multi-prefix sasl')
        self.assertSent(['CAP REQ :sasl'])
        bot.dispatch(':s CAP foo ACK :sasl')
        self.assertSent(['AUTHENTICATE PLAIN'])
        bot.dispatch('AUTHENTICATE +')
        self.assertSent(['AUTHENTICATE Zm9vAGZvbwBiYXI='])
        bot.dispatch(':s 903 foo :SASL authentication successful')
        self.assertSent(['CAP END'])

    def test_no_sasl(self):
        bot = self.callFTU(sasl_username='foo', sasl_password='bar')
        bot.notify('connection_ready')
        bot.dispatch(':s CAP * LS :multi-prefix')
        self.assertSent(['CAP END'])
