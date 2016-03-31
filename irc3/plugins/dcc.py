# -*- coding: utf-8 -*-
import irc3
from irc3.plugins import command
__doc__ = """
==============================================
:mod:`irc3.plugins.dcc` DCC Chat plugin
==============================================

This module provide a command to start a DCC CHAT with the bot and extend it
with CHAT commands.

CHAT Commands
=============

Adding new commands::

    >>> @dcc_command
    ... def echo(bot, mask, client, args):
    ...     '''echo command
    ...         %%echo <words>...
    ...     '''
    ...     yield ' '.join(args['words'])

bot is the bot instance. mask is the irc mask of the user connected via dcc.
client is an instance of :class:`~irc3.dcc.DCCChat`


API
===

.. autofunction:: dcc_command

.. autoclass:: Commands
   :members:

"""


def dcc_command(*func, **predicates):
    """DCC CHAT command decorator"""
    predicates['commands'] = 'irc3.plugins.dcc.Commands'
    if func:
        func = func[0]
        command.attach_command(func, **predicates)
        return func
    else:
        def wrapper(func):
            command.attach_command(func, **predicates)
            return func
        return wrapper


@irc3.plugin
class Commands(command.Commands):
    """DCC CHAT commands plugin"""

    requires = [command.__name__]

    @irc3.dcc_event(r'(\x01ACTION\s+|{re_cmd})(?P<cmd>\w+)'
                    r'((\s(?P<data>\S.*)|\x01)|(\x01|$))')
    def on_command(self, cmd, client=None, **kw):
        predicates, meth = self.get(cmd, (None, None))
        if meth is not None:
            return self.do_command(predicates, meth, client.mask, client, **kw)

    @dcc_command
    def help(self, *args):
        """Show help

            %%help [<cmd>]
        """
        return super(Commands, self).help(*args)

    @command.command(public=False, permission='dcc_chat')
    def chat(self, mask, *args):
        """DCC CHAT

            %%chat
        """
        self.context.create_task(self.context.dcc_chat(mask))
