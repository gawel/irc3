# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from irc3 import rfc
from irc3d.dec import event
from irc3d.dec import plugin
from irc3.plugins.command import Commands
from irc3.plugins.command import attach_command
__doc__ = '''
==============================================
:mod:`irc3d.plugins.command` Server commands
==============================================

Same as :mod:`~irc3.plugins.command` but for servers
'''


class server_policy(object):
    """Default server policy"""
    def __init__(self, context):
        self.context = context
        self.opers = context.config.get('opers', {})

    def check_oper_credentials(self, user, password):
        """return True if credential matches"""
        return self.opers.get(user, None) == password

    def __call__(self, predicates, meth, client, target, args, **kwargs):
        perm = predicates.get('permission', 'registered')
        if perm is not None and not client.registered:
            client.fwrite(rfc.ERR_NOTREGISTERED)
        elif str(perm).lower() == 'oper' and 'o' not in client.modes:
            client.fwrite(rfc.ERR_NOPRIVILEGES)
        else:
            return meth(client, args)


def command(*func, **predicates):
    predicates.setdefault('commands', __name__ + '.ServerCommands')
    predicates.setdefault('venusian_category', __name__)
    if func:
        func = func[0]
        attach_command(func, **predicates)
        return func
    else:
        def wrapper(func):
            attach_command(func, **predicates)
            return func
        return wrapper


@plugin
class ServerCommands(Commands):

    requires = ['irc3d.plugins.userlist']
    default_policy = server_policy
    case_sensitive = True

    @event(r'^(?P<cmd>\w+)(\s(?P<data>\S.*)|$)')
    def on_command(self, cmd, mask=None, target=None, client=None, **kw):
        cmd = cmd.upper()
        predicates, meth = self.get(cmd, (None, None))
        if meth is not None:
            self.do_command(predicates, meth, client, client, **kw)
        elif cmd not in ('MODE', 'USER', 'PRIVMSG', 'NOTICE'):
            client.fwrite(rfc.ERR_UNKNOWNCOMMAND, cmd=cmd)

    @command
    def OPER(self, client=None, args=None, **kwargs):
        """ The OPER command requires two arguments to be given. The first
        argument is the name of the operator as specified in the configuration
        file. The second argument is the password for the operator matching the
        name and host.

        The operator privileges are shown on a successful OPER.

            %%OPER <user> <password>
        """
        user = args['<user>']
        passwd = args['<password>']
        if self.guard.check_oper_credentials(user, passwd):
            self.context.log.warn('%r is now oper (%s)', client, user)
            client.modes.add('o')
            client.fwrite(rfc.RPL_YOUREOPER)
        else:
            self.context.log.warn('%r tried to be oper (%s)', client, user)
            client.fwrite(rfc.ERR_PASSWDMISMATCH)

    @command
    def HELP(self, client=None, args=None, **kwargs):
        """HELP displays the contents of the help file for topic requested.
        If no topic is requested, it will perform the equivalent to HELP index.

            %%HELP [<cmd>]
        """
        msgs = []
        cmd = (args['<cmd>'] or '').upper()
        if cmd and cmd != 'INDEX':
            predicates, meth = self.get(cmd, (None, None))
            if meth is not None:
                cmd = cmd.lower()
                index = '{c.srv} 705 {c.nick} ' + cmd + ' :'
                doc = meth.__doc__ or ''
                doc = [l.strip() for l in doc.split('\n') if l.strip()]
                for line in doc:
                    if '%%' in line:
                        line = line.strip('%')
                        msgs.insert(
                            0, '{c.srv} 704 {c.nick} ' + cmd + ' :' + line)
                    else:
                        msgs.append(index + line)
                msgs.append('{c.srv} 706 {c.nick} ' + cmd + ' :End of /HELP')
        else:
            index = '{c.srv} 705 {c.nick} index :'
            msgs.append(
                '{c.srv} 704 {c.nick} index :Help topics available to users:')
            cmds = []
            for cmd in sorted(self.keys()):
                cmds.append('{0:<16}'.format(cmd))
                if len(cmds) == 3:
                    msgs.append(index + ''.join(cmds).strip())
                    cmds = []
            if cmds:
                msgs.append(index + ''.join(cmds).strip())
            msgs.append('{c.srv} 706 {c.nick} index :End of /HELP')
        client.fwrite(msgs)
