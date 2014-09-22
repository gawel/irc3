# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__doc__ = '''
==============================================
:mod:`irc3d.plugins.command` Server commands
==============================================

Same as :mod:`~irc3.plugins.command` but for servers
'''
from irc3 import rfc
from irc3d.dec import event
from irc3d.dec import plugin
from irc3.plugins.command import Commands
from irc3.plugins.command import attach_command


@plugin
class ServerCommands(Commands):

    @event(r'^(?P<cmd>\w+)(\s(?P<data>\S.*)|$)')
    def on_command(self, cmd, mask=None, target=None, client=None, **kw):
        cmd = cmd.upper()
        predicates, meth = self.get(cmd, (None, None))
        if meth is not None:
            self.do_command(predicates, meth, client, client, **kw)
        elif cmd not in ('MODE', 'USER', 'PRIVMSG', 'NOTICE'):
            client.fwrite(rfc.ERR_UNKNOWNCOMMAND, cmd=cmd)


def command(*func, **predicates):
    predicates.setdefault('commands', ServerCommands)
    predicates.setdefault('venusian_category',
                          'irc3d.plugins.command')
    if func:
        func = func[0]
        attach_command(func, **predicates)
        return func
    else:
        def wrapper(func):
            attach_command(func, **predicates)
            return func
        return wrapper
