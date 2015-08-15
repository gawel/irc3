# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase


class TestCasefold(BotTestCase):

    config = dict(includes=['irc3.plugins.casefold'])

    def test_ascii(self):
        bot = self.callFTU(server_config={'CASEMAPPING': 'ascii'})

        self.assertEquals(bot.casefold('#testchan\\123[]56'),
                          '#testchan\\123[]56')
        self.assertEquals(bot.casefold('#tESt[]chAn'), '#test[]chan')
        self.assertEquals(bot.casefold('#TEsT\\CHaN'), '#test\\chan')

        self.assertEquals(bot.casefold(u'#TEsT\\CHaN'), u'#test\\chan')

    def test_rfc1459(self):
        bot = self.callFTU(server_config={'CASEMAPPING': 'rfc1459'})

        self.assertEquals(bot.casefold('#testchan\\123[]56'),
                          '#testchan|123{}56')
        self.assertEquals(bot.casefold('#tESt[]chAn'), '#test{}chan')
        self.assertEquals(bot.casefold('#TEsT\\CHaN'), '#test|chan')

        self.assertEquals(bot.casefold(u'#TEsT\\CHaN'), u'#test|chan')
