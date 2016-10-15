# -*- coding: utf-8 -*-
from irc3.plugins.command import command
import irc3
__doc__ = '''
==============================================
:mod:`irc3.plugins.search` Search plugin
==============================================

.. autoclass:: Search
'''


@irc3.plugin
class Search:

    requires = [
        __name__.replace('search', 'command'),
    ]

    headers = {
        'User-Agent': 'python-requests/irc3/search',
        'Cache-Control': 'max-age=0',
        'Pragma': 'no-cache',
    }

    def __init__(self, bot):
        self.bot = bot
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update(self.headers)
        except ImportError:  # pragma: no cover
            self.session = None

    @command(permission='view')
    def ddg(self, mask, target, args):
        """Search using https://duckduckgo.com/api

            %%ddg <query>...
        """
        q = ' '.join(args['<query>'])
        resp = self.session.get('http://api.duckduckgo.com/',
                                params=dict(q=q, format='json', t='irc3'),
                                allow_redirects=False)
        ctype = resp.headers['content-type']
        if 'json' in ctype or 'javascript' in ctype:
            if resp.status_code == 200:
                data = resp.json()
                return '{AbstractText} - {AbstractURL}'.format(**data)
            elif resp.status_code == 303:
                return 'Redirect to: {0}'.format(resp.headers['location'])
