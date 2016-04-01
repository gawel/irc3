# -*- coding: utf-8 -*-
import irc3
import requests
from irc3.plugins.command import command


@irc3.plugin
class SendFile(object):

    requires = [
        'irc3.plugins.command',
        'irc3.plugins.pager',
    ]

    def __init__(self, bot):
        self.bot = bot

    @command
    def cat(self, mask, target, args):
        """Cat a file with pagination

            %%cat
        """
        fd = open(__file__)
        for msg in self.bot.paginate(mask, fd, lines_per_page=10):
            yield msg

    @command
    def url(self, mask, target, args):
        """Cat an url with pagination

            %%url <url>
        """
        def iterator(url):
            resp = requests.get(url)
            for chunk in resp.iter_content(255):
                yield chunk.decode('utf8')
        for msg in self.bot.paginate(mask, iterator(args['<url>'])):
            yield msg
