# -*- coding: utf-8 -*-
import asyncio
from aiohttp import wsgi
from irc3 import plugin
import json


@plugin
class Webapp:

    requires = ['irc3.plugins.userlist']

    def __init__(self, bot):
        def server():
            return wsgi.WSGIServerHttpProtocol(self.wsgi)
        self.bot = bot
        loop = asyncio.get_event_loop()
        self.bot.log.info('Starting webapp')
        asyncio.Task(loop.create_server(
            server, '127.0.0.1', 5000))

    def wsgi(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'application/json')])
        plugin = self.bot.get_plugin('userlist')
        data = json.dumps(list(plugin.channels.keys()))
        return [data.encode('utf8')]
