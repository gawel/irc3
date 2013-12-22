# -*- coding: utf-8 -*-
import irc3
import signal
import logging.config
from irc3 import config


def main():
    logging.config.dictConfig(config.LOGGING)
    bots = []
    bot = irc3.IrcBot(nick='irc3', autojoins=['#irc3'],
                      host='irc.undernet.org', port=6667, ssl=False)
    bots.append(bot)
    bot.include('irc3.plugins.core')
    bot.include('irc3.plugins.log')
    bot.include('irc3.plugins.command')
    bot.include('irc3.plugins.human')
    bot.include('irc3.plugins.userlist')
    loop = bot.create_connection()
    loop.add_signal_handler(signal.SIGINT, loop.stop)
    loop.run_forever()

if __name__ == '__main__':
    main()
