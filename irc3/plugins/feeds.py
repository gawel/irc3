# -*- coding: utf-8 -*-
import os
import time
import irc3
import datetime
from concurrent.futures import ProcessPoolExecutor


def fetch(args):  # pragma: no cover
    import requests
    try:
        resp = requests.get(args['feed'], headers=args['headers'])
        with open(args['filename'], 'wb') as fd:
            fd.write(resp.content)
    finally:
        return args['name'], args['feed']


def parse(feedparser, args):
    try:
        with open(args['filename'] + '.updated') as fd:
            updated = fd.read().strip()
    except OSError:
        updated = '0'
    max_date = datetime.datetime.now() - datetime.timedelta(days=2)

    entries = []
    feed = feedparser.parse(args['filename'])
    for e in feed.entries:
        if e.updated <= updated:
            # skip already sent entries
            continue
        if datetime.datetime(*e.updated_parsed[:7]) < max_date:
            # skip entries older than 2 days
            continue
        entries.append((
            e.updated,
            dict(args,
                 title=e.title, link=e.link,
                 author=getattr(e, 'author', '') or '')))
    if entries:
        entries = sorted(entries)
        with open(args['filename'] + '.updated', 'w') as fd:
            fd.write(str(entries[-1][0]))
    return entries


@irc3.plugin
class Feeds:

    def __init__(self, bot):
        bot.feeds = self
        self.bot = bot
        config = bot.config.get(__name__, {})
        self.directory = os.path.expanduser(
            config.get('directory', '~/.irc3/feeds'))
        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)
        self.headers = {}
        self.feeds = {}
        for name, feed in config.items():
            if feed.startswith('http'):
                splited = feed.split('#')
                feed = dict(
                    name=str(name), feed=str(splited.pop(0)),
                    channels=['#' + c.strip('#,') for c in splited],
                    directory=self.directory,
                    filename=os.path.join(self.directory,
                                          name.replace('/', '_')),
                    headers=self.headers,
                    time=0)
                self.feeds[name] = feed

        self.max_workers = int(config.get('max_workers', 5))
        self.delay = int(config.get('delay', 2)) * 60
        self.fmt = '[{name}] {title} {link}'
        self.imports()

    def connection_made(self):  # pragma: no cover
        if not self.bot.config.testing:
            self.bot.loop.call_later(10, self.update)

    def imports(self):
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
        if entries is None:
            entries = []
        for feed in self.feeds.values():
            entries.extend(parse(self.feedparser, feed))
        for updated, e in sorted(entries, reverse=True):
            for channel in e['channels']:
                self.bot.privmsg(channel, self.fmt.format(**e))

    def fetch(self):  # pragma: no cover
        delay = time.time() - self.delay
        feeds = [f for f in self.feeds.values() if f['time'] < delay]
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            for name, feed in executor.map(fetch, feeds):
                self.bot.log.info('Feed %s %s fetched', name, feed)
                feed = self.feeds[name]
                feed['time'] = time.time()

    def update(self):  # pragma: no cover
        try:
            self.fetch()
        except Exception as e:
            self.bot.log.exception(e)
        try:
            self.parse()
        except Exception as e:
            self.bot.log.exception(e)
        self.bot.loop.call_later(self.delay, self.update)
