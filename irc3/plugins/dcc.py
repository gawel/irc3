# -*- coding: utf-8 -*-
import irc3
from irc3.plugins import command


def dcc_command(*func, **predicates):
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

    requires = ['irc3.plugins.command']

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
        def ctcp(f):
            protocol = f.result()
            self.context.ctcp(
                mask, 'DCC CHAT chat {0.host} {0.port}'.format(protocol))
        task = self.context.create_task(self.context.dcc_chat(mask))
        task.add_done_callback(ctcp)
