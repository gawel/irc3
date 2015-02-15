# -*- coding: utf-8 -*-
import os
import json
import irc3
import shelve
from ..compat import PY3
__doc__ = '''
==========================================
:mod:`irc3.plugins.storage` Storage plugin
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
    >>> del bot.db['mykey']
    >>> bot.db['mykey']
    {}

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
    >>> del bot.db['mykey']
    >>> bot.db['mykey']
    {}

..
    >>> bot.db.SIGINT()


Or redis::

    >>> config = ini2config("""
    ... [bot]
    ... includes =
    ...     irc3.plugins.storage
    ... storage = redis://localhost:6379/10
    ... """)
    >>> bot = IrcBot(**config)

..
    >>> bot.db.backend.flushdb()

Then use it::
    >>> bot.db.SIGINT()
    >>> bot.db['mykey'] = dict(key='value')
    >>> bot.db['mykey']
    {'key': 'value'}
    >>> del bot.db['mykey']
    >>> bot.db['mykey']
    {}


'''


class Shelve(object):

    def __init__(self, uri=None, **kwargs):
        self.filename = uri[9:]
        self.db = shelve.open(self.filename)

    def set(self, key, value):
        self.db[key] = value
        self.db.sync()

    def get(self, key):
        return self.db[key]

    def delete(self, key):
        del self.db[key]
        self.sync()

    def sync(self):
        self.db.sync()

    def close(self):
        self.db.close()


class JSON(object):

    def __init__(self, uri=None, **kwargs):
        self.filename = uri[7:]
        if os.path.isfile(self.filename):  # pragma: no cover
            with open(self.filename) as fd:
                self.db = json.load(fd)
        else:
            self.db = {}

    def set(self, key, value):
        self.db[key] = value
        self.sync()

    def get(self, key):
        return self.db[key]

    def delete(self, key):
        del self.db[key]
        self.sync()

    def sync(self):
        with open(self.filename, 'w') as fd:
            json.dump(self.db, fd, indent=2, sort_keys=True)

    def close(self):
        self.sync()


class Redis(object):

    def __init__(self, uri=None, **kwargs):
        ConnectionPool = irc3.utils.maybedotted(
            'redis.connection.ConnectionPool')
        pool = ConnectionPool.from_url(uri)
        StrictRedis = irc3.utils.maybedotted('redis.client.StrictRedis')
        self.db = StrictRedis(connection_pool=pool)

    def set(self, key, value):
        self.db.hmset(key, value)

    def get(self, key):
        keys = self.db.hkeys(key)
        if not keys:
            raise KeyError()
        values = self.db.hmget(key, keys)
        if PY3:
            keys = [k.decode('utf8') for k in keys]
            values = [v.decode('utf8') for v in values]
        values = dict(zip(keys, values))
        return values

    def delete(self, key):
        self.db.delete(key)

    def flushdb(self):
        self.db.flushdb()

    def sync(self):
        self.db.save()

    def close(self):
        self.sync()


@irc3.plugin
class Storage(object):

    backends = {
        'shelve': Shelve,
        'json': JSON,
        'unix': Redis,
        'redis': Redis,
        'rediss': Redis,
    }

    def __init__(self, context):
        uri = context.config.storage
        name = uri.split('://', 1)[0]
        try:
            factory = self.backends[name]
        except KeyError:  # pragma: no cover
            raise LookupError('No such backend %' % name)
        self.backend = factory(uri)
        self.context = context
        self.context.db = self

    def __setitem__(self, key, value):
        if not isinstance(value, dict):  # pragma: no cover
            raise TypeError('value must be a dict')
        try:
            return self.backend.set(key, value)
        except Exception as e:  # pragma: no cover
            self.bot.log.exception(e)
            raise

    def __getitem__(self, key):
        try:
            return self.backend.get(key)
        except KeyError:
            return {}
        except Exception as e:  # pragma: no cover
            self.bot.log.exception(e)
            raise

    def __delitem__(self, key):
        try:
            self.backend.delete(key)
        except Exception as e:  # pragma: no cover
            self.bot.log.exception(e)
            raise

    def SIGINT(self):
        self.backend.close()
