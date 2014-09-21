# -*- coding: utf-8 -*-
from irc3d.dec import plugin
from irc3d.dec import event
from irc3.plugins.command import Commands
from irc3.plugins.command import attach_command


@plugin
class ServerCommands(Commands):

    @event(r'^(?P<cmd>\w+)(\s(?P<data>\S.*)|$)')
    def on_command(self, cmd, mask=None, target=None, client=None, **kw):
        predicates, meth = self.get(cmd, (None, None))
        if meth is not None:
            self.do_command(predicates, meth, client, client, **kw)


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
