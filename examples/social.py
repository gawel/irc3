# -*- coding: utf-8 -*-
from irc3.plugins.command import command
import irc3
import json


class TwitterAdapter(object):

    def __init__(self, bot, conn):
        self.bot = bot
        self.conn = conn
        self.exc = irc3.utils.maybedotted('twitter.api.TwitterHTTPError')

    def __getattr__(self, attr):
        return getattr(self.conn, attr)

    def update_status(self, message):
        status = 'failure'
        res = self(self.conn.statuses.update, status=message)
        if isinstance(res, dict):
            if 'error' in res:
                status = res['error']
            elif 'id' in res:
                status = 'success'
        return status

    def __call__(self, meth, *args, **kwargs):
        try:
            res = meth(*args, **kwargs)
            if isinstance(res, dict):
                return res
            return dict(error=res)
        except self.exc as e:
            self.bot.log.exception(e)
            message = ''
            try:
                res = json.loads(e.response_data.decode('utf8'))
            except:
                pass
            else:
                message = ''
                for error in res.get('errors', []):
                    message += '{code}: {message}'.format(**error)
            if not message:
                message = e.response_data
            return dict(error=message)

    def __repr__(self):
        return '<TwitterAdapter for %r>' % self.conn


@irc3.plugin
class Social(object):

    requires = [
        'irc3.plugins.command',
    ]

    conn = dict(
    )

    networks = dict(
        twitter_stream=dict(
            adapter=TwitterAdapter,
            factory='twitter.TwitterStream',
            auth_factory='twitter.OAuth',
            domain='stream.twitter.com',
            api_version='1.1',
            secure=True
        ),
        twitter=dict(
            adapter=TwitterAdapter,
            factory='twitter.Twitter',
            auth_factory='twitter.OAuth',
            domain='api.twitter.com',
            api_version='1.1',
            secure=True
        ),
    )

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config.get(__name__, {})
        self.conns = irc3.utils.Config()
        for name, config in self.networks.copy().items():
            if 'twitter' in name:
                factory = self.twitter_factory
            else:
                factory = self.identica_factory
            conn = factory(config)
            if conn:
                self.conns[name] = conn
                self.bot.log.info('%s initialized', name)

    def twitter_factory(self, config):
        try:
            auth = irc3.utils.maybedotted(config.pop('auth_factory'))
            factory = irc3.utils.maybedotted(config.pop('factory'))
            adapter = irc3.utils.maybedotted(config.pop('adapter'))
        except LookupError as e:
            self.bot.log.exception(e)
        else:
            c = self.bot.config['twitter']
            config['auth'] = auth(c['token'], c['token_secret'],
                                  c['key'], c['secret'])
            return adapter(self.bot, factory(**config))

    def identica_factory(self, config):
        try:
            factory = irc3.utils.maybedotted(config.pop('factory'))
        except LookupError as e:
            self.bot.log.exception(e)
        else:
            c = self.bot.config['identica']
            return factory(c.pop('user'), **c)

    @command(permission='edit')
    def mb(self, mask, target, args):
        """Post to social networks

            %%mb [--id=<id>] <message>...
        """
        to = target == self.bot.nick and mask.nick or target
        message = ' '.join(args['<message>'])
        if args['--id'] and args['--id'] not in self.conns:
            return '{0} is an invalid id. Use {1}'.format(
                args['--id'],
                ', '.join([k for k in self.conns if 'stream' not in k]))
        for name, conn in self.conns.items():
            if 'stream' in name:
                continue
            if args['--id'] and args['--id'] != name:
                continue
            status = conn.update_status(message)
            self.bot.privmsg(to, '{0} {1}'.format(name, status))
