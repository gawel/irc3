# -*- coding: utf-8 -*-
import irc3


@irc3.event(r':(?P<ns>NickServ)!NickServ@services. NOTICE (?P<nick>irc3) :'
            r'This nickname is registered.*')
def register(bot, ns=None, nick=None):
    try:
        password = bot.config[bot.config.host][nick]
    except KeyError:
        pass
    else:
        bot.privmsg(ns, 'identify %s %s' % (nick, password))
