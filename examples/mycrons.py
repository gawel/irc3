# -*- coding: utf-8 -*-
from irc3.plugins.cron import cron


@cron('30 8 * * *')
def wakeup(bot):
    bot.privmsg('#irc3', "It's time to wake up!")


@cron('0 */2 * * *')
def take_a_break(bot):
    bot.privmsg('#irc3', "It's time to take a break!")
