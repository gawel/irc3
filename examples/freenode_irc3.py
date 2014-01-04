# -*- coding: utf-8 -*-
import os


class FeedsHook:
    """Custom hook for irc3.plugins.feeds"""

    def __init__(self, bot):
        self.bot = bot
        self.packages = ['asyncio', 'irc3']

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
            if entry.title.startswith(package):
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
