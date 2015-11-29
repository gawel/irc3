# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
import irc3


@irc3.plugin
class OldStyleClass:
    def __init__(self, bot):
        self.bot = bot


@irc3.plugin
class NewStyleClass(object):
    def __init__(self, bot):
        self.bot = bot


class TestPlugin(BotTestCase):

    def test_registration(self):
        bot = self.callFTU(includes=[__name__])
        plugin = bot.get_plugin(__name__ + '.OldStyleClass')
        assert isinstance(plugin, OldStyleClass)
        plugin = bot.get_plugin(__name__ + '.NewStyleClass')
        assert isinstance(plugin, NewStyleClass)
