import irc3
__doc__ = '''
==========================================
:mod:`irc3.plugins.web` Web plugin
==========================================

Introduce a web interface to post messages

Install aiohttp::

    $ pip install aiohttp

..
    >>> from irc3.testing import IrcBot
    >>> from irc3.testing import ini2config

Usage::

This example show how to define the web server config::

    >>> config = ini2config("""
    ... [bot]
    ... includes =
    ...     irc3.plugins.web
    ...
    ... [irc3.plugins.web]
    ... host = 127.0.0.1
    ... port = 8080
    ... api_key = toomanysecrets
    ... """)
    >>> bot = IrcBot(**config)

Then you'll be able to post a message to a channel using curl::

    $ curl -H "X-Api-Key: toomanysecrets" \
      --data Hello \
      http://127.0.0.1:8080/channels/irc3
'''


@irc3.plugin
class Web:

    def __init__(self, context):
        self.web = irc3.utils.maybedotted('aiohttp.web')
        self.context = context
        self.config = context.config.get(__name__, {})
        self.api_key = self.config.get('api_key')
        if not self.api_key:
            self.context.log.warning(
                'No web api_key is set. Your web service is insecure')
        self.channels = {}
        self.server = None

    def server_ready(self):
        if self.server is None:
            server = self.web.Server(self.handler, loop=self.context.loop)
            host = self.config.get('host', '127.0.0.1')
            port = int(self.config.get('port', 8080))
            self.context.log.info(
                'Starting web interface on %s:%s...', host, port)
            self.server = self.context.create_task(
                self.context.loop.create_server(server, host, port))

    @irc3.event(irc3.rfc.JOIN)
    def join(self, mask=None, channel=None, **kwargs):
        if mask.nick == self.context.nick:
            key = channel.strip('#&+')
            if key not in self.channels:
                self.channels[key] = channel

    async def handler(self, req):
        if req.method == 'POST':
            if self.api_key:
                if req.headers.get('X-Api-Key') != self.api_key:
                    return self.web.Response(status=403)
            if req.path.startswith('/channels/'):
                channel = req.path.strip('/').split('/')[-1]
                if channel in self.channels:
                    message = await req.text()
                    self.context.privmsg(self.channels[channel], message)
                    return self.web.Response(status=201)
                return self.web.Response(status=404)
        return self.web.Response()
