# -*- coding: utf-8 -*-
import irc3


@irc3.extend
def my_usefull_function(bot, *args):
    return 'my_usefull_function(*%s)' % (args,)


@irc3.plugin
class MyPlugin(object):

    def __init__(self, bot):
        self.bot = bot

    @irc3.extend
    def my_usefull_method(self, *args):
        return 'my_usefull_method(*%s)' % (args,)
