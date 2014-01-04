# -*- coding: utf-8 -*-
import os


class FeedsHook:
    """Custom hook for irc3.plugins.feeds"""

    def __init__(self, bot):
        self.bot = bot
        self.packages = ['asyncio', 'irc3']

    def reinit(self):
        self.travis = set()

    def filter_travis(self, feed, entry):
        """Only show the latest entry iif this entry is in a new state"""
        if feed.name not in self.travis:
            self.travis.add(feed.name)
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
                return feed, entry

    def filter_pypi(self, feed, entry):
        """Show only usefull packages"""
        for package in self.packages:
            if entry.title.startswith(package):
                return feed, entry

    def __call__(self, i, feed, entry):
        if not i:
            self.reinit()
        if feed.name.startswith('travis/'):
            return self.filter_travis(feed, entry)
        elif feed.name.startswith('pypi/'):
            return self.filter_pypi(feed, entry)
        return feed, entry
