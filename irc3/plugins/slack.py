import irc3
from irc3 import asyncio
import json
import re
import random
__doc__ = '''
==========================================
:mod:`irc3.plugins.slack` Slack plugin
==========================================

Introduce a slack/irc interface to bridge messages between slack and irc.

Install aiohttp::

    $ pip install aiohttp

Usage
=====

Create a bridge between slack and irc

..
    >>> from irc3.testing import IrcBot
    >>> from irc3.testing import ini2config
    >>> config = ini2config("""
    ... [bot]
    ... includes =
    ...     irc3.plugins.slack
    ... [irc3.plugins.slack]
    ... token = xoxb-slackbottoken
    ... notify =
    ...     U6DT2Q8HM
    ...     U3090DHMA
    ... [irc3.plugins.slack.channels]
    ... slack =
    ...     ${#}irc
    ... """)
    >>> bot = IrcBot(**config)

.. note::

    Be sure to invite the bot in slack to the channels it should be bridging


Config Options
==============

irc3.plugins.slack
------------------

token

    slack api token (user or bot integration)

notify

    The slack user ids to notify, this needs to be the unique user ids.

irc3.plugins.slack.channels
---------------------------

This section is a list of channels that should be bridge.  The first is the
slack channel that the bot needs to be joined to to bridge slack to irc.

Then assigned to that is the list of irc channels that slack channel should
forward to.
'''

EMOJIS = {
    "smile": ":)",
    "simple_smile": ":)",
    "smiley": ":-)",
    "grin": ":D",
    "wink": ";)",
    "smirk": ";)",
    "blush": ":$",
    "stuck_out_tongue": ":P",
    "stuck_out_tongue_winking_eye": ";P",
    "stuck_out_tongue_closed_eyes": "xP",
    "disappointed": ":(",
    "astonished": ":O",
    "open_mouth": ":O",
    "heart": "<3",
    "broken_heart": "</3",
    "confused": ":S",
    "angry": ">:(",
    "cry": ":,(",
    "frowning": ":(",
    "imp": "]:(",
    "innocent": "o:)",
    "joy": ":,)",
    "kissing": ":*",
    "laughing": "x)",
    "neutral_face": ":|",
    "no_mouth": ":-",
    "rage": ":@",
    "smiling_imp": "]:)",
    "sob": ":,'(",
    "sunglasses": "8)",
    "sweat": ",:(",
    "sweat_smile": ",:)",
    "unamused": ":$"
}


@irc3.plugin
class Slack:

    def __init__(self, bot):
        self.bot = bot
        self.client = irc3.utils.maybedotted('aiohttp.ClientSession')
        self.formdata = irc3.utils.maybedotted('aiohttp.FormData')
        self.config = self.bot.config.get(__name__, {})
        self.msgtype = irc3.utils.maybedotted('aiohttp.WSMsgType')
        self.client_response_error = irc3.utils.maybedotted(
            'aiohttp.client_exceptions.ClientResponseError'
        )
        self.channels = self.bot.config.get(
            '{0}.channels'.format(__name__), {}
        )
        self.clean_channels()  # remove has values from channels
        autojoins = set().union(*self.channels.values())
        self.bot.log.debug('Adding to autojoins list: {autojoins}')
        self.bot.config.setdefault('autojoins', []).extend(autojoins)
        self.matches = [
            (r'\n|\r\n|\r', ''),
            (r'<!channel>', '@channel'),
            (r'<!group>', '@group'),
            (r'<!everyone>', '@everyone'),
            (
                r'<#(?P<channelId>C\w+)\|?(?P<readable>\w+)?>',
                self.get_channel_by_id
            ),
            (
                r'<@(?P<userId>U\w+)\|?(?P<readable>\w+)?>',
                self.get_user_by_id
            ),
            (
                r':(?P<emoji>\w+):',
                self.get_emoji
            ),
            (r'<.+?\|(.+?)>', r'\g<1>'),
            (r'&lt', '<'),
            (r'&gt', '>'),
            (r'&amp', '&'),
        ]
        if 'token' not in self.config:
            self.bot.log.warning('No slack token is set.')

    def get_channel_by_id(self, matchobj):
        if matchobj.group('readable'):
            return matchobj.group('readable')
        future = asyncio.run_coroutine_threadsafe(
            self.api_call(
                'conversation.info',
                {'channel': matchobj.group('channelId')}
            ),
            loop=self.bot.loop
        )
        return '#{0}'.format(future.result()['channel']['name'])

    def get_user_by_id(self, matchobj):
        if matchobj.group('readable'):
            return matchobj.group('readable')
        future = asyncio.run_coroutine_threadsafe(
            self.api_call(
                'users.info',
                {'user': matchobj.group('userId')}
            ),
            loop=self.bot.loop
        )
        return '@{0}'.format(future.result()['user']['name'])

    def get_emoji(self, matchobj):
        emoji = matchobj.group('emoji')
        return EMOJIS.get(emoji, emoji)

    def clean_channels(self):
        self.channels.pop('#', None)
        self.channels.pop('hash', None)

    async def api_call(self, method, data=None):
        """Slack API call."""
        async with self.client(loop=self.bot.loop) as session:
            form = self.formdata(data or {})
            form.add_field('token', self.config['token'])
            async with session.post(
                'https://slack.com/api/{0}'.format(method), data=form
            ) as response:
                if response.status == 429:
                    await irc3.asyncio.sleep(
                        int(response.headers['Retry-After'])
                    )
                    return await self.api_call(method, data)
                if response.status != 200:
                    self.bot.log.debug('Error: %s', response)
                    raise Exception(
                        '{0} with {1} failed.'.format(method, data)
                    )
                return await response.json()

    def server_ready(self):
        self.bot.create_task(self.start())

    async def start(self):
        outbox = asyncio.Queue()
        asyncio.ensure_future(self.consumer(outbox.get), loop=self.bot.loop)
        while True:
            done, pending = await asyncio.wait(
                (self.producer(outbox.put), self.ping()),
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            if hasattr(self, 'ws'):
                del self.ws
            await self.notify_restart()
            await asyncio.sleep(5)

    async def notify_restart(self):
        if 'notify' not in self.config:
            return
        users = self.config['notify']
        if isinstance(users, str):
            users = [users]
        conversation = await self.api_call(
            'conversations.open',
            {'users': ','.join(users)}
        )
        await self.api_call('chat.postMessage', {
            'channel': conversation['channel']['id'],
            'text': 'irc3 has been restarted to reconnect to websocket',
        })

    async def parse_text(self, message):
        for match in self.matches:
            message = await self.bot.loop.run_in_executor(
                None, re.sub, match[0], match[1], message
            )
        return message

    async def ping(self):
        '''ping websocket'''
        while not hasattr(self, 'ws'):
            await asyncio.sleep(1)
        while True:
            msgid = random.randrange(10000)
            self.bot.log.debug('Sending ping message: {0}'.format(msgid))
            try:
                await self.ws.send_str(
                    json.dumps({'type': 'ping', 'id': msgid})
                )
            except self.client_response_error:
                break
            await asyncio.sleep(20)
            if msgid != self.msgid:
                break

    async def producer(self, put):
        rtm = await self.api_call('rtm.start')
        if not rtm['ok']:
            raise ConnectionError('Error connecting to RTM')
            self.bot.log.debug('Listening to Slack')
        async with self.client(loop=self.bot.loop) as session:
            async with session.ws_connect(rtm['url']) as self.ws:
                self.bot.log.debug('Listening to Slack')
                async for msg in self.ws:
                    if msg.type == self.msgtype.TEXT:
                        await put(json.loads(msg.data))
                    else:
                        break

    async def consumer(self, get):
        while True:
            message = await get()
            if message.get('type') == 'message':
                self.bot.log.debug(
                    'Message to irc: {0}'.format(message)
                )
                user = None
                if 'user' in message:
                    user = await self.api_call(
                        'users.info',
                        {'user': message['user']}
                    )
                    message['user'] = user['user']['name']
                func = getattr(
                    self,
                    '_handle_{0}'.format(message.get('subtype', 'default')),
                    None
                )
                if func is not None:
                    if 'channel' in message:
                        channel = await self.api_call(
                            'conversations.info',
                            {'channel': message['channel']}
                        )
                        message['channel'] = channel['channel']['name']
                    await func(message)
            elif message.get('type') == 'pong':
                self.bot.log.debug(
                    'Pong received: {0}'.format(message['reply_to'])
                )
                self.msgid = message['reply_to']
            else:
                self.bot.log.debug('Debug Message: %s', message)

    async def _handle_default(self, msg):
        for channel in self.channels.get(msg['channel'], []):
            await self.bot.privmsg(
                channel,
                '<{0}> {1}'.format(
                    msg['user'],
                    await self.parse_text(msg['text'])
                )
            )

    async def _handle_me_message(self, msg):
        for channel in self.channels.get(msg['channel'], []):
            await self.bot.action(
                channel,
                '<{0}> {1}'.format(
                    msg['user'],
                    await self.parse_text(msg['text'])
                )
            )

    @irc3.event(r'^(@(?P<tags>\S+) )?:'
                r'(?P<nick>\S+)!(?P<username>\S+)@(?P<hostmask>\S+) '
                r'(?P<event>(PRIVMSG|NOTICE)) '
                r'(?P<target>\S+) :(?P<data>.*)$')
    async def on_message(self, target=None, nick=None, data=None, **kwargs):
        self.bot.log.debug(
            'Match Data: {target} {nick} {data} {kwargs}'.format(**locals())
        )
        for channel, irc in self.channels.items():
            if target in irc:
                payload = {
                    'channel': channel,
                    'text': data,
                    'as_user': False,
                    'username': nick,
                    'icon_url': (
                        'http://api.adorable.io/avatars/48/'
                        '{0}.jpg'
                    ).format(nick),
                }
                await self.api_call('chat.postMessage', data=payload)
