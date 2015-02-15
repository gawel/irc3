Reloadable plugins
==================

irc3 provide a way to reload plugins without restarting the bot.

To do that, your plugin should provide a ``reload`` class method::

    class Plugin(object):

        def __init__(self, bot):
            self.bot = bot

        @classmethod
        def reload(cls, old):
            """this method should return a ready to use plugin instance.
            cls is the newly reloaded class. old is the old instance.
            """
            return cls(old.bot)

Plugins can also implement a few hooks to help taking care of reloads::

    class Plugin(object):

        def __init__(self, bot):
            self.bot = bot

        def before_reload(self):
            """Do stuff before reload"""

        def after_reload(self):
            """Do stuff after reload"""

..
    >>> from irc3.testing import IrcBot
    >>> bot = IrcBot(includes=['mycommands'])

To reload a plugin, just call the :func:`~irc3.IrcBot.reload` method with
module name(s) to reload::

    >>> bot.reload('mycommands')
