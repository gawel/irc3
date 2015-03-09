# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import time
import irc3
import datetime
from irc3.compat import isclass
from irc3.compat import asyncio
from concurrent.futures import ThreadPoolExecutor
from operator import itemgetter
__doc__ = '''
==========================================
:mod:`irc3.plugins.feeds` Feeds plugin
==========================================

Send a notification on channel on new feed entry.

Your config must looks like this:

.. code-block:: ini

    [bot]
    includes =
        irc3.plugins.feeds

    [irc3.plugins.feeds]
    channels = #irc3                             # global channel to notify
    delay = 5                                    # delay to check feeds
    directory = ~/.irc3/feeds                    # directory to store feeds
    hook = irc3.plugins.feeds.default_hook       # dotted name to a callable
    fmt = [{name}] {entry.title} - {entry.link}  # formatter

    # some feeds: name = url
    github/irc3 = https://github.com/gawel/irc3/commits/master.atom#irc3
    # custom formatter for the feed
    github/irc3.fmt = [{feed.name}] New commit: {entry.title} - {entry.link}
    # custom channels
    github/irc3.channels = #irc3dev #irc3
    # custom delay
    github/irc3.delay = 10

Hook is a dotted name refering to a callable (function or class) wich take a
list of entries as argument. It should yield the entries you want really show:

.. code-block:: python

    >>> def hook(entries):
    ...     for entry in entries:
    ...         if 'something bad' not in entry.title:
    ...             yield entry

    >>> class Hook:
    ...     def __init__(self, bot):
    ...         self.bot = bot
    ...     def __call__(self, entries):
    ...         for entry in entries:
    ...             if 'something bad' not in entry.title:
    ...                 yield entry


Here is a more complete hook used on freenode#irc3:

.. literalinclude:: ../../examples/freenode_irc3.py
   :pyobject: FeedsHook

'''


def default_hook(entries):
    """Default hook called for each entry"""
    return entries


def default_dispatcher(bot):  # pragma: no cover
    """Default messages dispatcher"""
    def dispatcher(messages):
        bot.call_many('privmsg', messages)
    return dispatcher


def fetch(args):
    """fetch a feed"""
    session = args['session']
    for feed, filename in zip(args['feeds'], args['filenames']):
        try:
            resp = session.get(feed, timeout=5)
            content = resp.content
        except:  # pragma: no cover
            pass
        else:
            with open(filename, 'wb') as fd:
                fd.write(content)
    return args['name']


def parse(feedparser, args):
    """parse a feed using feedparser"""
    entries = []
    args = irc3.utils.Config(args)
    max_date = datetime.datetime.now() - datetime.timedelta(days=2)

    for filename in args['filenames']:
        try:
            with open(filename + '.updated') as fd:
                updated = fd.read().strip()
        except (OSError, IOError):
            updated = '0'

        feed = feedparser.parse(filename)
        for e in feed.entries:
            if e.updated <= updated:
                # skip already sent entries
                continue
            try:
                updated_parsed = e.updated_parsed
            except AttributeError:
                continue
            if datetime.datetime(*updated_parsed[:7]) < max_date:
                # skip entries older than 2 days
                continue
            e['filename'] = filename
            e['feed'] = args
            entries.append((e.updated, e))
        if entries:
            entries = sorted(entries, key=itemgetter(0))
            with open(filename + '.updated', 'w') as fd:
                fd.write(str(entries[-1][0]))
    return entries


@irc3.plugin
class Feeds(object):
    """Feeds plugin"""

    PoolExecutor = ThreadPoolExecutor

    headers = {
        'User-Agent': 'python-requests/irc3/feeds',
        'Cache-Control': 'max-age=0',
        'Pragma': 'no-cache',
    }

    def __init__(self, bot):
        bot.feeds = self
        self.bot = bot

        config = bot.config.get(__name__, {})

        self.directory = os.path.expanduser(
            config.get('directory', '~/.irc3/feeds'))
        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)

        hook = config.get('hook', default_hook)
        hook = irc3.utils.maybedotted(hook)
        if isclass(hook):
            hook = hook(bot)
        self.hook = hook

        dispatcher = config.get('dispatcher', default_dispatcher)
        dispatcher = irc3.utils.maybedotted(dispatcher)
        self.dispatcher = dispatcher(bot)

        self.max_workers = int(config.get('max_workers', 5))
        delay = int(config.get('delay', 5))
        self.delay = delay * 60

        feed_config = dict(
            fmt=config.get('fmt', '[{feed.name}] {entry.title} {entry.link}'),
            delay=delay,
            channels=config.get('channels', ''),
            headers=self.headers,
            time=0,
        )

        self.feeds = {}
        for name, feed in config.items():
            if str(feed).startswith('http'):
                feeds = []
                filenames = []
                for i, feed in enumerate(irc3.utils.as_list(feed)):
                    filename = os.path.join(self.directory,
                                            name.replace('/', '_'))
                    filenames.append('{0}.{1}.feed'.format(filename, i))
                    feeds.append(feed)
                feed = dict(
                    feed_config,
                    name=str(name),
                    feeds=feeds,
                    filenames=filenames,
                    **irc3.utils.extract_config(config, str(name))
                )
                feed['delay'] = feed['delay'] * 60
                channels = irc3.utils.as_list(feed['channels'])
                feed['channels'] = [irc3.utils.as_channel(c) for c in channels]
                self.bot.log.debug(feed)
                self.feeds[name] = feed

        self.imports()

    def connection_made(self):
        """Initialize checkings"""
        self.bot.loop.call_later(10, self.update)

    def imports(self):
        """show some warnings if needed"""
        try:
            import feedparser
            self.feedparser = feedparser
        except ImportError:  # pragma: no cover
            self.bot.log.critical('feedparser is not installed')
            self.feedparser = None
        try:
            import requests
        except ImportError:  # pragma: no cover
            self.bot.log.critical('requests is not installed')
            self.session = None
        else:
            self.session = requests.Session()
            self.session.headers.update(self.headers)

    def parse(self, *args):
        """parse pre-fetched feeds and notify new entries"""
        entries = []
        for feed in self.feeds.values():
            self.bot.log.debug('Parsing feed %s', feed['name'])
            entries.extend(parse(self.feedparser, feed))

        def messages():
            for entry in self.hook([e for u, e in sorted(entries)]):
                if entry:
                    feed = entry.feed
                    message = feed['fmt'].format(feed=feed, entry=entry)
                    for c in feed['channels']:
                        yield c, message

        self.dispatcher(messages())

    def update_time(self, future):
        name = future.result()
        self.bot.log.debug('Feed %s fetched', name)
        feed = self.feeds[name]
        feed['time'] = time.time()

    def update(self):
        """update feeds"""
        loop = self.bot.loop
        loop.call_later(self.delay, self.update)

        now = time.time()
        session = self.session
        feeds = [dict(f, session=session) for f in self.feeds.values()
                 if f['time'] < now - f['delay']]
        if feeds:
            self.bot.log.info('Fetching feeds %s',
                              ', '.join([f['name'] for f in feeds]))
            tasks = []
            for feed in feeds:
                task = loop.run_in_executor(None, fetch, feed)
                task.add_done_callback(self.update_time)
                tasks.append(task)
            task = self.bot.create_task(
                asyncio.wait(tasks, timeout=len(feeds) * 2, loop=loop))
            task.add_done_callback(self.parse)
