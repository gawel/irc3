# -*- coding: utf-8 -*-
from irc3.plugins.command import command


@command
def echo(bot, mask, target, args):
    """Echo command

        %%echo <words>...
    """
    bot.privmsg(mask.nick, ' '.join(args['<words>']))
