# -*- coding: utf-8 -*-
import irc3


@irc3.event(r'(@(?P<tags>\S+) )?:(?P<ns>NickServ)!NickServ@services.'
            r' NOTICE (?P<nick>irc3) :This nickname is registered.*')
def register(bot, ns=None, nick=None, **kw):
    try:
        password = bot.config[bot.config.host][nick]
    except KeyError:
        pass
    else:
        bot.privmsg(ns, 'identify %s %s' % (nick, password))
