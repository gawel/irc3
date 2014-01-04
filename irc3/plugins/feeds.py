# -*- coding: utf-8 -*-
__doc__ = '''
==========================================
:mod:`irc3.plugin.feeds` Feeds plugin
==========================================

Send a notification on channel on new feed entry.

Your config must looks like this:

.. code-block:: ini

    [bot]
    includes =
        irc3.plugins.feeds

    [irc3.plugins.feeds]
    delay = 5                                    # delay to check feeds
    directory = ~/.irc3/feeds                    # directory to store feeds
    hook = irc3.plugins.feeds.default_hook       # dotted name to a callable
    fmt = [{name}] {entry.title} - {entry.link}  # formater

    # some feeds: name = http://url#channel,#channel2
    github/irc3 = https://github.com/gawel/irc3/commits/master.atom#irc3
    # custom formater for the feed
    github/irc3.fmt = [{name}] New commit by {e.author}: {e.title} - {e.link}

Hook is a dotted name refering to a callable (function or class) wich take 3
arguments: ``index, feed, entry``. If the callable return None then the entry
is skipped:

.. code-block:: python

    >>> def hook(i, feed, entry):
    ...     if 'something bad' in entry.title:
    ...         return None
    ...     return feed, entry

    >>> class Hook:
    ...     def __init__(self, bot):
    ...         self.bot = bot
    ...     def __call__(self, i, feed, entry):
    ...         if 'something bad' in entry.title:
    ...             return None
    ...         return feed, entry

'''
import os
import time
import irc3
import datetime
from concurrent.futures import ThreadPoolExecutor


def default_hook(i, feed, entry):
    """Default hook called for each entry"""
    return feed, entry


def fetch(args):  # pragma: no cover
    """fetch a feed"""
    import requests
    try:
        resp = requests.get(args['feed'], headers=args['headers'])
        with open(args['filename'], 'wb') as fd:
            fd.write(resp.content)
    finally:
        return args['name'], args['feed']


def parse(feedparser, args):
    """parse a feed using feedparser"""
    try:
        with open(args['filename'] + '.updated') as fd:
            updated = fd.read().strip()
    except OSError:
        updated = '0'
    max_date = datetime.datetime.now() - datetime.timedelta(days=2)

    entries = []
    feed = feedparser.parse(args['filename'])
    args = irc3.utils.Config(args)
    for e in feed.entries:
        if e.updated <= updated:
            # skip already sent entries
            continue
        if datetime.datetime(*e.updated_parsed[:7]) < max_date:
            # skip entries older than 2 days
            continue
        entries.append((e.updated, (args, e)))
    if entries:
        entries = sorted(entries)
        with open(args['filename'] + '.updated', 'w') as fd:
            fd.write(str(entries[-1][0]))
    return entries


@irc3.plugin
class Feeds:
    """Feeds plugin"""

    headers = {'User-Agent': 'python-requests/irc3'}

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

        fmt = config.get('fmt', '[{feed.name}] {entry.title} {entry.link}')
        self.max_workers = int(config.get('max_workers', 5))
        self.delay = int(config.get('delay', 5)) * 60

        self.feeds = {}
        for name, feed in config.items():
            if str(feed).startswith('http'):
                splited = feed.split('#')
                feed = dict(
                    name=str(name), feed=str(splited.pop(0)),
                    channels=['#' + c.strip('#,') for c in splited],
                    directory=self.directory,
                    filename=os.path.join(self.directory,
                                          name.replace('/', '_')),
                    headers=self.headers,
                    fmt=config.get(name + '.fmt', fmt),
                    time=0)
                self.feeds[name] = feed

        self.imports()

    def connection_made(self):  # pragma: no cover
        """Initialize checkings"""
        if not self.bot.config.testing:
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
            import requests  # NOQA
        except ImportError:  # pragma: no cover
            self.bot.log.critical('requests is not installed')

    def parse(self, entries=None):
        """parse pre-fetched feeds and notify new entries"""
        if entries is None:
            entries = []
        for feed in self.feeds.values():
            entries.extend(parse(self.feedparser, feed))
        for i, (updated, entry) in enumerate(sorted(entries)):
            entry = self.hook(i, *entry)
            if not entry:
                continue
            feed, entry = entry
            for channel in feed['channels']:
                try:
                    self.bot.privmsg(
                        channel,
                        feed['fmt'].format(feed=feed, entry=entry))
                except Exception as e:  # pragma: no cover
                    self.bot.log.exception(e)

    def fetch(self):  # pragma: no cover
        """prefetch feeds"""
        delay = time.time() - self.delay
        feeds = [f for f in self.feeds.values() if f['time'] < delay]
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for name, feed in executor.map(fetch, feeds):
                self.bot.log.debug('Feed %s %s fetched', name, feed)
                feed = self.feeds[name]
                feed['time'] = time.time()

    def update(self):  # pragma: no cover
        """fault tolerent fetch and notify"""
        try:
            self.fetch()
        except Exception as e:
            self.bot.log.exception(e)
        try:
            self.parse()
        except Exception as e:
            self.bot.log.exception(e)
        self.bot.loop.call_later(self.delay, self.update)
