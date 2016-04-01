# -*- coding: utf-8 -*-
from irc3.plugins.command import command
from irc3 import asyncio
import irc3
import time
__doc__ = '''
===============================================
:mod:`irc3.plugins.pager` Paginate large output
===============================================

Usage
=====

.. literalinclude:: ../../examples/paginate.py

API
===

.. autoclass:: Paginate

'''


class Page(object):

    def __init__(self, mask, iterator, first_page=4, lines_per_page=10):
        self.mask = mask
        self.iterator = iterator
        self.first_page = first_page
        self.lines_per_page = lines_per_page
        self.page = 0
        self.ended = False
        self.time = time.time()

    def get(self):
        self.time = time.time()
        self.ended = True
        i = 0
        if not self.page:
            size = self.first_page
        else:
            size = self.lines_per_page
        self.page += 1
        for msg in self.iterator:
            yield msg
            i += 1
            if size and i >= size:
                self.ended = False
                break
        if self.ended:
            self.close()
            yield '.'

    def close(self):
        try:
            self.iterator.close()
        except:
            pass


@irc3.plugin
class Paginate(object):
    """Pagination plugin"""

    requires = [command.__module__]

    def __init__(self, context):
        self.context = context
        self.pages = {}
        self.expiration_delay = 60
        self.context.create_task(self.clean_old_pages())

    @asyncio.coroutine
    def clean_old_pages(self):  # pragma: no cover
        self.context.log.debug('Cleaning old pages...')
        t = time.time()
        d = []
        for k, v in self.pages.items():
            if v.time + self.expiration_delay > t:
                d.append(k)
        for k in d:
            page = self.pages[k]
            page.close()
        yield from asyncio.sleep(60, loop=self.context.loop)
        yield from self.clean_old_pages()

    @irc3.extend
    def paginate(self, mask, iterator, first_page=None, lines_per_page=10):
        """Paginate large output. Available as ``IrcBot.paginate()``"""
        first_page = first_page or self.context.config.flood_burst
        lines_per_page = lines_per_page or 0
        page = Page(mask, iterator,
                    first_page=first_page, lines_per_page=lines_per_page)
        for msg in page.get():
            yield msg
        if not page.ended:
            self.pages[mask] = page

    @command
    def more(self, mask, target, args):
        '''Get more data from the latest command

        %%more
        '''
        page = self.pages.get(mask)
        if page is None:
            yield 'Sorry. I have nothing left for you'
        else:
            for msg in page.get():
                yield msg
            if page.ended:
                del self.pages[mask]
