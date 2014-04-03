# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from irc3.plugins.command import command


@command
def echo(bot, mask, target, args):
    """Echo command

        %%echo <words>...
    """
    bot.privmsg(mask.nick, ' '.join(args['<words>']))


@command(permission='admin', public=False)
def adduser(bot, mask, target, args):
    """Add a user

        %%adduser <name> <password>
    """
    bot.privmsg(mask.nick, 'User added')
