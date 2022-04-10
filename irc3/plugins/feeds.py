# -*- coding: utf-8 -*-
import os
import time
import irc3
import datetime
from irc3.compat import asyncio

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
    channels = #irc3                          # global channel to notify
    delay = 5                                 # delay to check feeds in minutes
    directory = ~/.irc3/feeds                 # directory to store feeds
    hook = irc3.plugins.feeds.default_hook       # dotted name to a callable
    fmt = [{name}] {entry.title} - {entry.link}  # formatter

    # some feeds: name = url
    github/irc3 = https://github.com/gawel/irc3/commits/master.atom#irc3
    # custom formatter for the feed
    github/irc3.fmt = [{feed.name}] New commit: {entry.title} - {entry.link}
    # custom channels
    github/irc3.channels = #irc3dev #irc3
    # custom delay in minutes
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

HEADERS = {
    'User-Agent': 'python-aiohttp/irc3/feeds',
    'Cache-Control': 'max-age=0',
    'Pragma': 'no-cache',
}


def default_hook(entries):
    """Default hook called for each entry"""
    return entries


def default_dispatcher(bot):  # pragma: no cover
    """Default messages dispatcher"""
    def dispatcher(messages):
        bot.call_many('privmsg', messages)
    return dispatcher


ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"


def parse(feedparser, args):
    """parse a feed using feedparser"""
    entries = []
    args = irc3.utils.Config(args)
    max_date = datetime.datetime.now() - datetime.timedelta(days=2)

    for filename in args['filenames']:
        try:
            with open(filename + '.updated', encoding="UTF-8") as fd:
                updated = datetime.datetime.strptime(
                    fd.read()[:len("YYYY-MM-DDTHH:MM:SS")], ISO_FORMAT
                )
        except (OSError, IOError, ValueError):
            updated = datetime.datetime(datetime.MINYEAR, 1, 1)

        feed = feedparser.parse(filename)
        for e in feed.entries:
            try:
                updated_parsed = datetime.datetime(*e.updated_parsed[:6])
            except AttributeError:
                continue
            if updated_parsed <= updated:
                # skip already sent entries
                continue
            if updated_parsed < max_date:
                # skip entries older than 2 days
                continue
            e['filename'] = filename
            e['feed'] = args
            entries.append((e.updated, e))
        if entries:
            most_recent_entry = max(
                entries, key=lambda entry: entry[1].updated_parsed
            )
            most_recent_date = datetime.datetime(
                *most_recent_entry[1].updated_parsed[:6]
            )
            with open(filename + '.updated', 'w') as fd:
                fd.write(most_recent_date.isoformat())
    return entries


@irc3.plugin
class Feeds:
    """Feeds plugin"""

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
        if isinstance(hook, type):
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
        self.bot.create_task(self.periodically_update())

    async def periodically_update(self):
        """After a connection has been made, call update feeds periodically."""
        if not self.aiohttp or not self.feedparser:
            return
        await asyncio.sleep(10)
        while True:
            await self.update()
            await asyncio.sleep(self.delay)

    def imports(self):
        """show some warnings if needed"""
        try:
            import feedparser
            self.feedparser = feedparser
        except ImportError:  # pragma: no cover
            self.bot.log.critical('feedparser is not installed')
            self.feedparser = None
        try:
            import aiohttp
        except ImportError:  # pragma: no cover
            self.bot.log.critical('aiohttp is not installed')
            self.aiohttp = None
        else:
            self.aiohttp = aiohttp

    def parse(self):
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
                    for channel in feed['channels']:
                        yield channel, message

        self.dispatcher(messages())

    async def update(self):
        """update feeds"""
        now = time.time()
        feeds = [feed for feed in self.feeds.values()
                 if feed['time'] < now - feed['delay']]
        if not feeds:
            return
        self.bot.log.info('Fetching feeds %s',
                          ', '.join([f['name'] for f in feeds]))
        timeout = self.aiohttp.ClientTimeout(total=5)
        async with self.aiohttp.ClientSession(timeout=timeout) as session:
            await asyncio.gather(
                *[self.fetch(feed, session) for feed in feeds]
            )
        self.parse()

    async def fetch(self, feed, session):
        """fetch a feed"""
        for url, filename in zip(feed['feeds'], feed['filenames']):
            try:
                async with session.get(url, headers=HEADERS) as resp:
                    with open(filename, 'wb') as file:
                        file.write(await resp.read())
            except Exception:  # pragma: no cover
                self.bot.log.exception(
                    "Exception while fetching feed %s", feed['name']
                )
        self.bot.log.debug('Feed %s fetched', feed['name'])
        feed['time'] = time.time()
