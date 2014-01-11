# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.testing import MagicMock
from irc3.plugins import cron


class Cron(object):

    def __init__(self, bot):
        pass

    @cron.cron('* * * * *')
    def raiser(bot):
        raise RuntimeError()


class TestCron(BotTestCase):

    config = dict(includes=['irc3.plugins.cron'])

    def setUp(self):
        cron.Cron.start_time = 0

    def test_cron(self):
        bot = self.callFTU()
        bot.loop = MagicMock()
        bot.include('mycrons')
        plugin = bot.get_plugin(cron.Crons)
        plugin.log.setLevel(1000)
        plugin.connection_made()
        self.assertEqual(len(plugin), 2, plugin)
        self.assertTrue(bot.loop.call_at.call_count, 2)

        bot.loop.reset_mock()
        plugin.call_cron(plugin[1])
        self.assertTrue(bot.loop.call_at.call_count, 1)

    def test_cron_raise(self):
        bot = self.callFTU()
        bot.loop = MagicMock()
        bot.include(__name__)
        plugin = bot.get_plugin(cron.Crons)
        plugin.log.setLevel(1000)
        plugin.connection_made()
        self.assertEqual(len(plugin), 1, plugin)
        self.assertTrue(bot.loop.call_at.call_count, 1)

        bot.loop.reset_mock()
        plugin.call_cron(plugin[0])
        self.assertTrue(bot.loop.call_at.call_count, 1)
