# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from irc3.testing import BotTestCase
from irc3.compat import asyncio


class TestAsync(BotTestCase):

    name = 'irc3.plugins.async'
    config = dict(includes=[name], loop=asyncio.get_event_loop())

    def test_whois_fail(self):
        bot = self.callFTU()
        assert len(bot.events_re['in']) == 0
        task = bot.async.whois(nick='gawel')
        assert len(bot.events_re['in']) > 2
        bot.dispatch(':localhost 401 me gawel :No such nick')
        bot.loop.run_until_complete(task)
        result = task.result()
        assert result['success'] is False
        assert len(bot.events_re['in']) == 0

    def test_whois_success(self):
        bot = self.callFTU()
        assert len(bot.events_re['in']) == 0
        task = bot.async.whois(nick='GaWel')
        assert len(bot.events_re['in']) > 2
        bot.dispatch(':localhost 311 me gawel username localhost * :realname')
        bot.dispatch(':localhost 318 me gawel :End')
        bot.loop.run_until_complete(task)
        assert len(bot.events_re['in']) == 0
        result = task.result()
        assert result['success']
        assert result['timeout'] is False
        assert result['username'] == 'username'
        assert result['realname'] == 'realname'

    def test_whois_timeout(self):
        bot = self.callFTU()
        assert len(bot.events_re['in']) == 0
        task = bot.async.whois(nick='GaWel', timeout=.1)
        assert len(bot.events_re['in']) > 2
        bot.loop.run_until_complete(task)
        result = task.result()
        assert result['timeout'] is True

    def test_ison(self):
        bot = self.callFTU()
        assert len(bot.events_re['in']) == 0
        task = bot.async.ison('GaWel', timeout=.1)
        assert len(bot.events_re['in']) > 0
        bot.dispatch(':localhost 303 me :gawel')
        bot.loop.run_until_complete(task)
        result = task.result()
        assert result['timeout'] is False
        assert result['nicknames'] == ['gawel']
