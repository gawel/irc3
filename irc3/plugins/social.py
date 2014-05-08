# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__doc__ = '''
==============================================
:mod:`irc3.plugins.social` Social networking
==============================================

Add ``tweet`` and ``retweet`` commands.

Extend the bot with ``.get_social_connection()`` and ``.search_tweets()``.

..
    >>> from irc3.testing import IrcBot

Usage::

    >>> bot = IrcBot(
    ...     includes=['irc3.plugins.social'],
    ...     twitter=dict(key='yourkey', secret='yoursecret',
    ...                  token='yourtoken', token_secret='yoursecret')
    ... )
    >>> bot.get_social_connection()
    <TwitterAdapter for <twitter.api.Twitter object at ...>>

Api:

.. autoclass:: Social
   :members:

'''
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

    def format(self, item):
        text = item['text'].replace('\n', ' ')
        return '@{screen_name}: {text}'.format(text=text, **item['user'])

    def __call__(self, meth, *args, **kwargs):
        try:
            res = meth(*args, **kwargs)
            if isinstance(res, dict):
                return res
            return dict(error=res)
        except self.exc as e:  # pragma: no cover
            self.bot.log.exception(e)
            message = ''
            try:
                res = json.loads(e.response_data.decode('utf8'))
            except:
                pass
            else:
                message = ''
                errors = res.get('errors', [])
                if isinstance(errors, list):
                    for error in errors:
                        message += '{code}: {message}'.format(**error)
                elif isinstance(errors, str):
                    message += errors
            if not message:
                message = e.response_data
            return dict(error=message)

    def __repr__(self):
        return '<TwitterAdapter for %r>' % self.conn


@irc3.plugin
class Social(object):
    """The social plugin"""

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
            else:  # pragma: no cover
                factory = self.identica_factory
            conn = factory(config.copy())
            if conn:
                self.conns[name] = conn
                self.bot.log.info('%s initialized', name)

    def twitter_factory(self, config):
        try:
            auth = irc3.utils.maybedotted(config.pop('auth_factory'))
            factory = irc3.utils.maybedotted(config.pop('factory'))
            adapter = irc3.utils.maybedotted(config.pop('adapter'))
        except LookupError as e:  # pragma: no cover
            self.bot.log.exception(e)
        else:
            c = self.bot.config['twitter']
            config['auth'] = auth(c['token'], c['token_secret'],
                                  c['key'], c['secret'])
            return adapter(self.bot, factory(**config))

    def identica_factory(self, config):  # pragma: no cover
        # not really implemented for now
        try:
            factory = irc3.utils.maybedotted(config.pop('factory'))
        except LookupError as e:
            self.bot.log.exception(e)
        else:
            c = self.bot.config['identica']
            return factory(c.pop('user'), **c)

    @irc3.extend
    def get_social_connection(self, network='twitter'):
        """return a connection object for the network:

        - A Twitter instance from
          https://github.com/sixohsix/twitter/tree/master

        """
        return self.conns[network]

    @command(permission='edit')
    def tweet(self, mask, target, args):
        """Post to social networks

            %%tweet [--net=<network>] <message>...
        """
        to = target == self.bot.nick and mask.nick or target
        message = ' '.join(args['<message>'])
        if args['--net'] and args['--net'] not in self.conns:
            return '{0} is an invalid network. Use {1}'.format(
                args['--net'],
                ', '.join([k for k in self.conns if 'stream' not in k]))
        for name, status in self.send_tweet(message, network=args['--net']):
            self.bot.privmsg(to, '{0} {1}'.format(name, status))

    @irc3.extend
    def send_tweet(self, message, network=None):
        """Send a tweet to networks"""
        for name, conn in self.conns.items():
            if 'stream' in name:
                continue
            if network and network != name:  # pragma: no cover
                continue
            status = 'failure'
            res = conn(conn.statuses.update, status=message)
            if isinstance(res, dict):
                if 'error' in res:
                    status = res['error']
                elif 'id' in res:
                    status = 'success'
            yield name, status

    @command(permission='edit')
    def retweet(self, mask, target, args):
        """Retweet

            %%retweet [--net=<network>] <url_or_id>
        """
        if args['--net'] and args['--net'] not in self.conns:
            return '{0} is an invalid network. Use {1}'.format(
                args['--net'],
                ', '.join([k for k in self.conns if 'stream' not in k]))
        else:
            args['--net'] = 'twitter'
        to = target == self.bot.nick and mask.nick or target
        conn = self.get_social_connection(args['--net'])
        tid = args['<url_or_id>'].strip('/')
        tid = tid.split('/')[-1]
        res = conn(getattr(conn.statuses.retweet, tid))
        if 'error' in res:
            self.bot.privmsg(
                to, '{0}: {1[error]}'.format(args['--net'], res))
        elif 'id' in res:
            self.bot.privmsg(
                to, conn.format(res))

    @irc3.extend
    def search_tweets(self, q=None, **kwargs):
        """Search for tweets on twitter"""
        conn = self.get_social_connection(network='twitter')
        try:
            results = conn.search.tweets(q=q, **kwargs)
        except Exception as e:
            self.bot.log.exception(e)
        else:
            if isinstance(results, dict):
                return results.get('statuses', [])
        return []
