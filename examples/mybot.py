# -*- coding: utf-8 -*-
import signal
import logging.config
from irc3.plugins.command import command
from irc3.dec import plugin
from irc3.dec import event
from irc3 import rfc
from irc3 import config
import irc3


@plugin
class MyPlugin:
    """A plugin is a class which take the IrcBot as argument
    """

    def __init__(self, bot):
        self.bot = bot

    @event(rfc.JOIN)
    def welcome(self, mask, channel):
        """Welcome people who join a channel"""
        bot = self.bot
        if mask.nick != self.bot.nick:
            bot.privmsg(channel, 'Welcome %s!' % mask.nick)

    @command
    def echo(self, mask, target, args):
        """Echo command

            %%echo <words>...
        """
        self.bot.privmsg(mask.nick, ' '.join(args['<words>']))


def main():
    # logging configuration
    logging.config.dictConfig(config.LOGGING)

    # instanciate a bot
    bot = irc3.IrcBot(nick='irc3', autojoins=['#irc3'],
                      host='irc.undernet.org', port=6667, ssl=False)
    bot.include('irc3.plugins.core')
    bot.include('irc3.plugins.command')
    bot.include(__name__)  # this register MyPlugin

    # create an asyncio connection
    loop = bot.create_connection()

    # start the loop
    loop.add_signal_handler(signal.SIGINT, loop.stop)
    loop.run_forever()

if __name__ == '__main__':
    main()
