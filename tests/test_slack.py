# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.plugins import slack


class TestSlack(BotTestCase):

    config = dict(includes=['irc3.plugins.slack'])

    def test_simple_matches(self):
        bot = self.callFTU()
        plugin = bot.get_plugin(slack.Slack)
        self.assertEqual('', plugin.parse_text('\n'))
        self.assertEqual('', plugin.parse_text('\r\n'))
        self.assertEqual('', plugin.parse_text('\r'))
        self.assertEqual('@channel', plugin.parse_text('<!channel>'))
        self.assertEqual('@group', plugin.parse_text('<!group>'))
        self.assertEqual('@everyone', plugin.parse_text('<!everyone>'))
        self.assertEqual('<', plugin.parse_text('&lt'))
        self.assertEqual('>', plugin.parse_text('&gt'))
        self.assertEqual('&', plugin.parse_text('&amp'))
        self.assertEqual('daniel', plugin.parse_text('<WHATEVER|daniel>'))

    def test_channel_matches(self):
        bot = self.callFTU()
        plugin = bot.get_plugin(slack.Slack)
        plugin.slack_channels = {
            'C12345': {'name': 'testchannel'},
        }
        self.assertEqual('#testchannel', plugin.parse_text('<#C12345>'))
        self.assertEqual('channel', plugin.parse_text('<#C12345|channel>'))

    def test_user_matches(self):
        bot = self.callFTU()
        plugin = bot.get_plugin(slack.Slack)
        plugin.slack_users = {
            'U12345': 'daniel',
        }
        self.assertEqual('@daniel', plugin.parse_text('<@U12345>'))
        self.assertEqual('user', plugin.parse_text('<@U12345|user>'))

    def test_emoji_matches(self):
        bot = self.callFTU()
        plugin = bot.get_plugin(slack.Slack)
        self.assertEqual(':-)', plugin.parse_text(':smiley:'))
        self.assertEqual(':@', plugin.parse_text(':rage:'))

    def test_channels(self):
        bot = self.callFTU()
        plugin = bot.get_plugin(slack.Slack)
        self.assertNotIn('#', plugin.channels)
        self.assertNotIn('hash', plugin.channels)
