# -*- coding: utf-8 -*-
from irc3.plugins.cron import cron
import os


class FeedsHook(object):
    """Custom hook for irc3.plugins.feeds"""

    def __init__(self, bot):
        self.bot = bot
        self.packages = [
            'asyncio', 'irc3', 'panoramisk',
            'requests', 'trollius', 'webtest',
            'pyramid',
        ]

    def filter_travis(self, entry):
        """Only show the latest entry iif this entry is in a new state"""
        fstate = entry.filename + '.state'
        if os.path.isfile(fstate):
            with open(fstate) as fd:
                state = fd.read().strip()
        else:
            state = None
        if 'failed' in entry.summary:
            nstate = 'failed'
        else:
            nstate = 'success'
        with open(fstate, 'w') as fd:
            fd.write(nstate)
        if state != nstate:
            build = entry.title.split('#')[1]
            entry['title'] = 'Build #{0} {1}'.format(build, nstate)
            return True

    def filter_pypi(self, entry):
        """Show only usefull packages"""
        for package in self.packages:
            if entry.title.lower().startswith(package):
                return entry

    def __call__(self, entries):
        travis = {}
        for entry in entries:
            if entry.feed.name.startswith('travis/'):
                travis[entry.feed.name] = entry
            elif entry.feed.name.startswith('pypi/'):
                yield self.filter_pypi(entry)
            else:
                yield entry
        for entry in travis.values():
            if self.filter_travis(entry):
                yield entry


@cron('*/15 * * * *')
def auto_retweet(bot):
    """retweet author tweets about irc3 and pypi releases"""
    conn = bot.get_social_connection(id='twitter')
    dirname = os.path.expanduser('~/.irc3/twitter/{nick}'.format(**bot.config))

    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    filename = os.path.join(dirname, 'retweeted')
    if os.path.isfile(filename):
        with open(filename) as fd:
            retweeted = [i.strip() for i in fd.readlines()]
    else:
        retweeted = []

    for user in ('pypi', 'gawel_'):
        results = conn.search.tweets(
            q=user + ' AND irc3',
            result_type='recent')
        for item in results.get('statuses', []):
            if item['user']['screen_name'] == user:
                if item['id_str'] not in retweeted:
                    res = conn(getattr(conn.statuses.retweet, item['id_str']))
                    if 'id' in res:
                        with open(filename, 'a+') as fd:
                            fd.write(item['id_str'] + '\n')


@cron('*/2 * * * *', venusian_category='irc3.debug')
def test_cron(bot):
    bot.log.info('Running test_cron')


@cron('*/3 * * * *', venusian_category='irc3.debug')
def test_cron_raise(bot):
    raise OSError('test_cron_raise')
