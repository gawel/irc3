# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from irc3.plugins.command import command
from collections import defaultdict
from irc3.compat import text_type
import logging
import irc3


class default_resolver(object):
    """A really simple resolver to show how you must handle accounts and phone
    numbers"""

    db = dict(
        lukhas=dict(login='lukhas',
                    fullname='Lucas Bonnet',
                    channel='SIP/lukhas',
                    exten='lukhas',
                    context='default'),
        gawel=dict(login='gawel',
                   fullname='Gael Pasgrimaud',
                   channel='SIP/gawel',
                   exten='gawel',
                   context='default'))

    def __init__(self, bot):
        self.bot = bot

    def __call__(self, mask, value):
        if value.isdigit():
            return dict(
                exten=value,
                channel='IAX2/your-provider/' + value,
                fullname='External call ' + value,
                context='default')
        else:
            return self.db.get(value)


def lower_header_keys(obj):
    values = list(obj.headers.items())
    for k, v in values:
        obj.headers[k.lower()] = v


@irc3.plugin
class Asterisk(object):

    requires = ['irc3.plugins.command']

    def __init__(self, bot):
        self.bot = bot
        self.bot.asterirc = self
        self.config = config = dict(
            host='127.0.0.1',
            port=5038,
            http_port='8088',
            protocol='http'
        )
        config.update(bot.config.get('asterisk', {}))
        self.log = logging.getLogger('irc3.ast')
        self.ilog = logging.getLogger('irc.asterirc')
        self.ilog.set_irc_targets(bot, self.config['channel'])
        self.log.info('Channel is set to {channel}'.format(**config))
        self.rooms = defaultdict(dict)
        self.http = None
        self.manager = None
        self.manager_url = None
        self.resolver = irc3.utils.maybedotted(self.config['resolver'])
        if isinstance(self.resolver, type):
            self.resolver = self.resolver(bot)

    def connection_made(self):
        self.bot.loop.call_later(1, self.connect)

    def post_connect(self):
        if 'use_http' not in self.config:
            success, resp = self.send_command('http show status', debug=False)
            if success:
                host, port, path = None, None, None
                for line in resp.lines:
                    if line.startswith('Server Enabled and Bound to'):
                        host = line.split(' ')[-1]
                        host, port = host.split(':')
                        self.config.update(http_port=port)
                    elif '/arawman' in line:
                        path = True
                if host and port and path:
                    self.config['use_http'] = 'true'

        if self.config.get('use_http', 'false') == 'true':
            self.manager_url = (
                '{protocol}://{host}:{http_port}/arawman'
            ).format(**self.config)
            success, resp = self.send_command('http show status', debug=False)
            if success:
                self.log.info('switching manager calls to %s',
                              self.manager_url)
            else:
                self.config['use_http'] = 'false'
                self.log.error('not able to use %s (%s)',
                               self.manager_url, resp)
        self.update_meetme()

    def update_meetme(self):
        success, resp = self.send_command('meetme list')
        if success:
            if 'No active MeetMe conferences.' in resp.lines:
                self.rooms = defaultdict(dict)
        else:
            self.bot.loop.call_later(2, self.post_connect)

    def connect(self):
        config = self.config
        if self.manager is not None:
            self.manager.close()
        try:
            Manager = irc3.utils.maybedotted('asterisk.manager.Manager')
            self.manager = manager = Manager()
            manager.connect(config['host'], config['port'])
            manager.login(config['username'], config['secret'])
            manager.register_event('Shutdown', self.handle_shutdown)
            manager.register_event('Meetme*', self.handle_meetme)
            if config.get('debug'):
                manager.register_event('*', self.handle_event)
            resp = manager.send_action({'Action': 'Status', 'Channel': ''})
            status = resp.get_header('Response', '').lower()
            if status in ('success', 'follows'):
                self.log.debug('connected')
                self.bot.loop.call_later(1, self.post_connect)
                return True
            self.log.critical('connect failed: %r', resp.headers)
        except Exception as resp:
            self.log.exception(resp)
        self.log.info('connect retry in 5s')
        self.bot.loop.call_later(5, self.connect)

    def handle_shutdown(self, event, manager):
        manager.close()
        self.bot.loop.call_later(2, self.connect)

    def handle_event(self, event, manager):
        self.log.debug('handle_event %s %s', event, event.headers)

    def handle_meetme(self, event, manager):
        self.log.debug('handle_meetme %s %s', event, event.headers)
        lower_header_keys(event)
        name = event.name.lower()
        room = event.get_header('meetme')

        if name == 'meetmeend':
            if room in self.rooms:
                del self.rooms[room]
            self.ilog.info('room {} is closed.'.format(room))
            return

        action = None
        caller = event.get_header('calleridname')
        if 'external call' in caller.lower():
            caller += ' ' + event.get_header('calleridnum')
        if 'join' in name:
            action = 'join'
            self.rooms[room][caller] = event.get_header('usernum')
        elif 'leave' in name:
            action = 'leave'
            if caller in self.rooms.get(room, []):
                del self.rooms[room][caller]

        if action:
            # log
            args = dict(caller=caller, action=action,
                        room=room, total=len(self.rooms[room]))
            self.ilog.info((
                '{caller} has {action} room {room} '
                '(total in this room: {total})').format(**args))

    def send_action_via_http(self, cdict, **kwargs):
        if not self.http:
            self.http = irc3.utils.maybedotted('requests.Session')()
            auth = (self.config['username'], self.config['secret'])
            auth = irc3.utils.maybedotted(
                'requests.auth.HTTPDigestAuth')(*auth)
            self.http.auth = auth
        resp = self.http.get(self.manager_url, params=cdict)
        self.http.cookies = []
        if resp.status_code != 200:
            return False, resp.reason
        for line in resp.text.strip('\r\n').split('\r\n'):
            line = line.strip()
            if ':' in line:
                k, v = line.split(':', 1)
                resp.headers[k] = v
            else:  # pragma: no cover
                if isinstance(line, text_type):  # pragma: no cover
                    line = line.encode(resp.encoding)
                resp._content = line.encode('utf8')
        return True, resp

    def send_action_via_manager(self, cdict, **kwargs):
        if self.manager is None or not self.manager.connected:
            if not self.connect():
                return (False,
                        'Not able to connect to server. Please retry later')
        try:
            resp = self.manager.send_action(cdict, **kwargs)
        except Exception as e:
            self.log.error('send_action(%r, **%r)', cdict, kwargs)
            self.log.exception(e)
            return False, 'Sorry an error occured. ({})'.format(repr(e))
        else:
            lower_header_keys(resp)
            status = resp.get_header('response').lower()
            resp.text = resp.data
            return status in ('success', 'follows'), resp

    def send_action(self, *args, **kwargs):
        if self.config.get('use_http', 'false') == 'true':
            send_action = self.send_action_via_http
        else:
            send_action = self.send_action_via_manager
        return send_action(*args, **kwargs)

    def send_command(self, command, debug=False):
        st, resp = self.send_action({'Action': 'Command', 'Command': command})
        if debug:
            self.log.debug('Command "%s" => Succeed: %s, Data:\n%s',
                           command, st, getattr(resp, 'text', resp))
        if st:
            resp.lines = []
            if resp.headers.get('response', '').lower() == 'follows':
                resp.lines = resp.text.split('\n')
        return st, resp

    @command(permission='voip')
    def call(self, mask, target, args):
        """Call someone. Destination and from can't contains spaces.

            %%call <destination> [<from>]

        """
        if 'nick' not in args:
            args['nick'] = mask.nick

        self.log.info('call %s %s %s', mask, target, args)
        callee = self.resolver(mask, args['<destination>'])
        if args['<from>']:
            caller = self.resolver(mask, args['<from>'])
        else:
            caller = self.resolver(mask, mask.nick)

        if caller is None or caller.get('channel') is None:
            return '{nick}: Your caller is invalid.'.format(**args)
        if callee is None or callee.get('exten') is None:
            return '{nick}: Your destination is invalid.'.format(**args)

        action = {
            'Action': 'Originate',
            'Channel': caller['channel'],
            'WaitTime': 20,
            'CallerID': caller.get('fullname', caller['channel']),
            'Exten': callee['exten'],
            'Context': caller.get('context', 'default'),
            'Priority': 1,
        }
        success, resp = self.send_action(action)
        if success:
            return '{nick}: Call to {<destination>} done.'.format(**args)
        else:
            return resp

    @command(permission='voip')
    def room(self, mask, target, args):
        """Invite/kick someone in a room. You can use more than one
        destination. Destinations can't contains spaces.

            %%room (list|invite|kick) [<room>] [<destination>...]

        """
        self.log.info('room %s %s %s', mask, target, args)
        args['nick'] = mask.nick
        room = args['<room>']
        print(args)
        if args['invite']:

            callees = args['<destination>']
            message = '{nick}: {<from>} has been invited to room {<room>}.'
            if not callees:
                callees = [mask.nick]
                message = '{nick}: You have been invited to room {<room>}.'

            resolved = [self.resolver(mask, c) for c in callees]
            if None in resolved:
                callees = zip(resolved, callees)
                invalid = [c for r, c in callees if r is None]
                yield (
                    "{0}: I'm not able to resolve {1}. Please fix it!"
                ).format(mask.nick, ', '.join(invalid))
                raise StopIteration()

            for callee in callees:
                args['<destination>'] = args['<room>']
                args['<from>'] = callee
                msg = self.call(mask, target, args)
                if 'Call to' in msg:
                    yield message.format(**args)
                else:
                    yield msg

        if room and room not in self.rooms:
            yield 'Invalid room'
            raise StopIteration()

        if args['list']:
            if room:
                messages = ['Room {0}: {1}'.format(room, u)
                            for u in self.rooms[room]]
            else:
                messages = []
                for room, users in self.rooms.items():
                    messages.extend(['Room {0}: {1}'.format(room, u)
                                     for u in self.rooms[room]])
            if messages:
                for message in messages:
                    yield message
            else:
                yield 'Nobody here.'

        elif args['kick']:
            users = self.rooms[room]
            commands = []
            for victim in args['<destination>']:
                for user in users:
                    if victim.lower() in user.lower():
                        peer = users[user]
                        commands.append((
                            user,
                            'meetme kick {0} {1}'.format(room, peer)))

            if not commands:
                yield 'No user matching query'
                raise StopIteration()

            for user, command in commands:
                success, resp = self.send_command(command)
                if success:
                    del self.rooms[room][user]
                    yield '{0} kicked from {1}.'.format(user, room)
                else:  # pragma: no cover
                    yield 'Failed to kick {0} from {1}.'.format(user, room)

    @command(permission='voip')
    def voip(self, mask, target, args):
        """Show voip status

            %%voip status [<id>]
        """
        self.log.info('voip %s %s %s', mask, target, args)
        args['nick'] = mask.nick
        if args['<id>']:
            peer = self.resolver(mask.nick, args['<id>'])
        else:
            peer = self.resolver(mask, mask.nick)
        if peer is None:
            return '{nick}: Your id is invalid.'.format(**args)
        action = {'Action': 'SIPshowpeer', 'peer': peer['login']}
        success, resp = self.send_action(action)
        if success:
            return ('{nick}: Your VoIP phone is registered. '
                    '(User Agent: {sip-useragent} on {address-ip})'
                    ).format(nick=mask.nick, **resp.headers)

    @command(permission='admin', venusian_category='irc3.debug')
    def asterisk(self, mask, target, args):  # pragma: no cover
        """Send a raw command to asterisk. Use "help" to list core commands.

            %%asterisk <command>...
        """
        cmd = ' '.join(args['<command>'])
        cmd = dict(
            help='core show help',
        ).get(cmd, cmd)
        status, resp = self.send_command(cmd, debug=True)
        return status and 'Success' or 'Failed'

    @command(permission='admin', venusian_category='irc3.debug')
    def asterisk_originate(self, mask, target, args):  # pragma: no cover
        """Send raw originate

            %%asterisk_originate <Channel> <CallerID> <Exten> <Context>
        """
        action = {
            'Action': 'Originate',
            'WaitTime': 20,
            'Priority': 1,
        }
        for k, v in list(args.items()):
            if k.startswith('<'):
                action[k.strip('<>')] = v
        status, resp = self.send_action(action)
        return 'Action {} sent'.format(repr(action))

    def SIGINT(self):
        if self.manager is not None:
            self.manager.close()
        self.log.info('SIGINT: connection closed')
