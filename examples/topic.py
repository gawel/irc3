# -*- coding: utf-8 -*-
import irc3
from irc3.plugins.command import command
from irc3.plugins.cron import cron


@irc3.plugin
class TopicPlugin:

    requires = ['irc3.plugins.async']

    def __init__(self, bot):
        self.bot = bot

    @irc3.event(irc3.rfc.TOPIC)
    @irc3.event(irc3.rfc.RPL_TOPIC)
    def get_topic(self, channel=None, data=None, **kwargs):
        """check the topic on join or on user action"""
        self.bot.log.warn('Topic for %s is %s', channel, data)

    @cron('* * * * *')
    @irc3.asyncio.coroutine
    def cron_topic(self):
        """check the topic each minute"""
        result = yield from self.bot.async_cmds.topic('#irc3_dev')
        self.bot.log.warn('Topic for #irc3_dev is %(topic)s', result)

    @command
    def topic(self, mask, target, args):
        """Set topic

        %%topic <topic>...
        """
        if target.is_channel:
            self.bot.topic(target, ' '.join(args['<topic>']))

    @command
    @irc3.asyncio.coroutine
    def aiotopic(self, mask, target, args):
        """Set topic and get result the async way

        %%aiotopic [<topic>...]
        """
        if target.is_channel:
            result = yield from self.bot.async_cmds.topic(
                target, ' '.join(args['<topic>']))
            return result['topic']
