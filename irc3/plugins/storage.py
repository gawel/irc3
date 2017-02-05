# -*- coding: utf-8 -*-
import os

try:
    import ujson as json
except ImportError:
    import json

import irc3
import shelve
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
    >>> 'mykey' in bot.db
    True
    >>> bot.db['mykey']
    {'key': 'value'}
    >>> bot.db.setdefault('mykey', key='default')
    {'key': 'value'}
    >>> bot.db.setdefault('mykey', item='default')
    {'item': 'default'}
    >>> bot.db.set('mykey', item='value')
    >>> bot.db.setdefault('mykey', item='default')
    {'item': 'value'}
    >>> del bot.db['mykey']
    >>> bot.db.get('mykey')
    >>> bot.db.get('mykey', 'default')
    'default'
    >>> bot.db['mykey']
    Traceback (most recent call last):
      ...
    KeyError: 'mykey'
    >>> 'mykey' in bot.db
    False
    >>> bot.db.setlist('mylist', ['foo', 'bar'])
    >>> bot.db.getlist('mylist')
    ['foo', 'bar']
    >>> del bot.db['mylist']

You can use an instance as key::

    >>> class MyPlugin:
    ...     pass
    >>> plugin = MyPlugin()
    >>> bot.db[plugin] = dict(key='value')
    >>> bot.db[plugin]
    {'key': 'value'}
    >>> del bot.db[plugin]
    >>> bot.db.get(plugin)

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
    >>> bot.db.get('mykey')
    >>> bot.db.setlist('mylist', ['foo', 'bar'])
    >>> bot.db.getlist('mylist')
    ['foo', 'bar']
    >>> del bot.db['mylist']

..
    >>> bot.db.getlist('mylist', ['foo', 'bar'])
    ['foo', 'bar']
    >>> bot.db.setlist('mylist', ['foo', 'bar'])
    >>> bot.db.setlist('mylist', ['foo', 'bar'])
    >>> del bot.db['mylist']
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
    >>> bot.db.backend.flushdb()  # require redis
    >>> bot.db.SIGINT()

Then use it::

    >>> bot.db['mykey'] = dict(key='value')
    >>> bot.db['mykey']
    {'key': 'value'}
    >>> del bot.db['mykey']
    >>> bot.db.get('mykey')
    >>> bot.db['mykey']
    Traceback (most recent call last):
      ...
    KeyError: 'mykey'
    >>> bot.db.setlist('mylist', ['foo', 'bar'])
    >>> bot.db.getlist('mylist')
    ['foo', 'bar']
    >>> del bot.db['mylist']

Api
===

.. autoclass:: Storage
  :members: __getitem__,__setitem__,__delitem__,__contains__,get,set,setdefault

'''


class Shelve:

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

    def contains(self, key):
        return key in self.db

    def sync(self):
        self.db.sync()

    def close(self):
        self.db.close()


class JSON:

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

    def contains(self, key):
        return key in self.db

    def sync(self):
        with open(self.filename, 'w') as fd:
            json.dump(self.db, fd, indent=2, sort_keys=True)

    def close(self):
        self.sync()


class Redis:

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
        keys = [k.decode('utf8') for k in keys]
        values = [v.decode('utf8') for v in values]
        values = dict(zip(keys, values))
        return values

    def delete(self, key):
        self.db.delete(key)

    def contains(self, key):
        return self.db.exists(key)

    def flushdb(self):
        self.db.flushdb()

    def sync(self):
        self.db.save()

    def close(self):
        self.sync()


@irc3.plugin
class Storage:

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

    def setdefault(self, key_, **kwargs):
        """Update storage value for key with kwargs iif the keys doesn't
        exist. Return stored values"""
        stored = self[key_]
        changed = False
        for k, v in kwargs.items():
            if k not in stored:
                stored[k] = v
                changed = True
            else:
                kwargs[k] = stored[k]
        if changed:
            self[key_] = stored
        return kwargs

    def get(self, key_, default=None):
        """Get storage value for key or return default"""
        if key_ not in self:
            return default
        else:
            return self[key_]

    def getlist(self, key_, default=None):
        """Get storage value (as list) for key or return default"""
        if key_ not in self:
            return default
        else:
            value = self[key_]
            value = [(int(i), v) for i, v in value.items()]
            return [v for k, v in sorted(value)]

    def set(self, key_, **kwargs):
        """Update storage value for key with kwargs"""
        stored = self.get(key_, dict())
        changed = False
        for k, v in kwargs.items():
            if k not in stored or stored[k] != v:
                stored[k] = v
                changed = True
        if changed:
            self[key_] = stored

    def setlist(self, key_, value):
        """Update storage value (as list)"""
        value = dict([(str(i), v) for i, v in enumerate(value)])
        if key_ in self:
            del self[key_]
        self.set(key_, **value)

    def __setitem__(self, key, value):
        """Set storage value for key"""
        key = getattr(key, '__module__', key)
        if not isinstance(value, dict):  # pragma: no cover
            raise TypeError('value must be a dict')
        try:
            return self.backend.set(key, value)
        except Exception as e:  # pragma: no cover
            self.context.log.exception(e)
            raise

    def __getitem__(self, key):
        """Get storage value for key"""
        key = getattr(key, '__module__', key)
        try:
            return self.backend.get(key)
        except KeyError:
            raise KeyError(key)
        except Exception as e:  # pragma: no cover
            self.context.log.exception(e)
            raise

    def __delitem__(self, key):
        """Delete key in storage"""
        key = getattr(key, '__module__', key)
        try:
            self.backend.delete(key)
        except Exception as e:  # pragma: no cover
            self.context.log.exception(e)
            raise

    def __contains__(self, key):
        """Return True if storage contains key"""
        key = getattr(key, '__module__', key)
        try:
            return self.backend.contains(key)
        except Exception as e:  # pragma: no cover
            self.context.log.exception(e)
            raise

    def SIGINT(self):
        self.backend.close()
