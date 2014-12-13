# -*- coding: utf-8 -*-
__doc__ = '''
==========================================
:mod:`irc3.plugins.storage` Cron plugin
==========================================

Add a ``db`` attribute to the bot

..
    >>> from irc3.testing import IrcBot
    >>> from irc3.testing import ini2config
    >>> import tempfile
    >>> fd = tempfile.NamedTemporaryFile(prefix='irc3', suffix='.db')
    >>> db_file = fd.name
    >>> fd.close()
    >>> fd = tempfile.NamedTemporaryFile(prefix='irc3', suffix='.json')
    >>> json_file = fd.name
    >>> fd.close()

Usage::

    >>> config = ini2config("""
    ... [bot]
    ... includes =
    ...     irc3.plugins.storage
    ... storage = json://%s
    ... """ % json_file)
    >>> bot = IrcBot(**config)

Then use it::

    >>> bot.db['mykey'] = dict(key='value')
    >>> bot.db['mykey']
    {'key': 'value'}

..
    >>> bot.db.SIGINT()

You can also use shelve::

    >>> config = ini2config("""
    ... [bot]
    ... includes =
    ...     irc3.plugins.storage
    ... storage = shelve://%s
    ... """ % db_file)
    >>> bot = IrcBot(**config)
    >>> bot.db['mykey'] = dict(key='value')
    >>> bot.db['mykey']
    {'key': 'value'}

..
    >>> bot.db.SIGINT()

Or redis::

    >>> config = ini2config("""
    ... [bot]
    ... includes =
    ...     irc3.plugins.storage
    ... storage = redis://localhost:6379/1
    ... """)
    >>> bot = IrcBot(**config)


'''
import os
import json
import irc3
import shelve


class Shelve(object):

    def __init__(self, uri=None, **kwargs):
        self.filename = uri[9:]
        self.db = shelve.open(self.filename)

    def hmset(self, key, value):
        self.db[key] = value
        self.db.sync()

    def hmget(self, key):
        return self.db[key]

    def sync(self):
        self.db.sync()

    def close(self):
        self.db.close()


class JSON(object):

    def __init__(self, uri=None, **kwargs):
        self.filename = uri[7:]
        if os.path.isfile(self.filename):
            with open(self.filename) as fd:
                self.db = json.load(fd)
        else:
            self.db = {}

    def hmset(self, key, value):
        self.db[key] = value
        self.sync()

    def hmget(self, key):
        return self.db[key]

    def sync(self):
        with open(self.filename, 'w') as fd:
            json.dump(self.db, fd, indent=2, sort_keys=True)

    def close(self):
        self.sync()


def redis_backend(uri):
    ConnectionPool = irc3.utils.maybedotted('redis.connection.ConnectionPool')
    pool = ConnectionPool.from_url(uri)
    StrictRedis = irc3.utils.maybedotted('redis.client.StrictRedis')
    return StrictRedis(connection_pool=pool)


@irc3.plugin
class Storage(object):

    backends = {
        'shelve': Shelve,
        'json': JSON,
        'unix': redis_backend,
        'redis': redis_backend,
        'rediss': redis_backend,
    }

    def __init__(self, context):
        uri = context.config.storage
        name = uri.split('://', 1)[0]
        try:
            factory = self.backends[name]
        except KeyError:
            raise LookupError('No such backend %' % name)
        self.backend = factory(uri)
        self.context = context
        self.context.db = self

    def __setitem__(self, key, value):
        if not isinstance(value, dict):
            raise TypeError('value must be a dict')
        return self.backend.hmset(key, value)

    def __getitem__(self, key):
        return self.backend.hmget(key)

    def SIGINT(self):
        if hasattr(self.backend, 'close'):
            self.backend.close()
