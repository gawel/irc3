# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from irc3.testing import BotTestCase
from irc3.compat import asyncio


class TestAsync(BotTestCase):

    name = 'irc3.plugins.async'
    config = dict(includes=[name], loop=asyncio.get_event_loop())

    def test_whois_fail(self):
        bot = self.callFTU()
        assert len(bot.registry.events_re['in']) == 0
        task = bot.async_cmds.whois(nick='gawel')
        assert len(bot.registry.events_re['in']) > 2
        bot.dispatch(':localhost 401 me gawel :No such nick')
        bot.loop.run_until_complete(task)
        result = task.result()
        assert result['success'] is False
        assert len(bot.registry.events_re['in']) == 0

    def test_whois_success(self):
        bot = self.callFTU()
        assert len(bot.registry.events_re['in']) == 0
        task = bot.async_cmds.whois(nick='GaWel')
        assert len(bot.registry.events_re['in']) > 2
        bot.dispatch(':localhost 311 me gawel username localhost * :realname')
        bot.dispatch(':localhost 319 me gawel :@#irc3')
        bot.dispatch(':localhost 312 me gawel localhost :Paris, FR')
        bot.dispatch(':localhost 671 me gawel :is using a secure connection')
        bot.dispatch(':localhost 330 me gawel gawel :is logged in as')
        bot.dispatch(':localhost 318 me gawel :End')
        bot.loop.run_until_complete(task)
        assert len(bot.registry.events_re['in']) == 0
        result = task.result()
        assert result['success']
        assert result['timeout'] is False
        assert result['username'] == 'username'
        assert result['realname'] == 'realname'

    def test_whois_timeout(self):
        bot = self.callFTU()
        assert len(bot.registry.events_re['in']) == 0
        task = bot.async_cmds.whois(nick='GaWel', timeout=.1)
        assert len(bot.registry.events_re['in']) > 2
        bot.loop.run_until_complete(task)
        result = task.result()
        assert result['timeout'] is True

    def test_who_channel(self):
        bot = self.callFTU()
        assert len(bot.registry.events_re['in']) == 0
        task = bot.async_cmds.who('#irc3')
        assert len(bot.registry.events_re['in']) == 2
        bot.dispatch(
            ':card.freenode.net 352 nick #irc3 ~irc3 host1 srv1 irc3 H :0 bot')
        bot.dispatch(
            ':card.freenode.net 352 nick #irc3 ~gael host2 srv2 gawel H@ :1 g')
        bot.dispatch(':card.freenode.net 315 nick #irc3 :End of /WHO list.')
        bot.loop.run_until_complete(task)
        result = task.result()
        assert result['timeout'] is False
        assert len(result['users']) == 2

    def test_who_nick(self):
        bot = self.callFTU()
        assert len(bot.registry.events_re['in']) == 0
        task = bot.async_cmds.who('irc3')
        assert len(bot.registry.events_re['in']) == 2
        bot.dispatch(
            ':card.freenode.net 352 nick * ~irc3 host1 serv1 irc3 H :0 bot')
        bot.dispatch(':card.freenode.net 315 nick irc3 :End of /WHO list.')
        bot.loop.run_until_complete(task)
        result = task.result()
        assert result['timeout'] is False
        assert result['hopcount'] == '0'

    def test_ison(self):
        bot = self.callFTU()
        assert len(bot.registry.events_re['in']) == 0
        task = bot.async_cmds.ison('GaWel', timeout=.1)
        assert len(bot.registry.events_re['in']) > 0
        bot.dispatch(':localhost 303 me :gawel')
        bot.loop.run_until_complete(task)
        result = task.result()
        assert result['timeout'] is False
        assert result['names'] == ['gawel']

    def test_names(self):
        bot = self.callFTU()
        assert len(bot.registry.events_re['in']) == 0
        task = bot.async_cmds.names('#irc3')
        assert len(bot.registry.events_re['in']) == 2
        bot.dispatch(
            ':card.freenode.net 353 nick @ #irc3 :irc3 @gawel')
        bot.dispatch(
            ':card.freenode.net 353 nick @ #irc3 :+panoramisk')
        bot.dispatch(
            ':card.freenode.net 366 nick #irc3 :End of /NAMES list.')
        bot.loop.run_until_complete(task)
        result = task.result()
        assert result['timeout'] is False
        assert len(result['names']) == 3
