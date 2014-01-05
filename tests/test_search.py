# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase


class TestSearch(BotTestCase):

    config = dict(includes=['irc3.plugins.search'])

    def test_ddg(self):
        self.patch_requests(
            status_code=200,
            headers={'content-type': 'application/json'},
            json=dict(AbstractText='Yo', AbstractURL='http://'),
        )
        bot = self.callFTU()
        bot.dispatch(':g!u@h PRIVMSG #chan :!ddg cuisine')
        self.assertSent(['PRIVMSG #chan :Yo - http://'])

    def test_ddg_redirect(self):
        self.patch_requests(
            status_code=303,
            headers={'content-type': 'application/json',
                     'location': 'http://google'},
        )
        bot = self.callFTU()
        bot.dispatch(':g!u@h PRIVMSG #chan :!ddg cuisine')
        self.assertSent(['PRIVMSG #chan :Redirect to: http://google'])
