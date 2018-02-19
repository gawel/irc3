import aiohttp
import irc3
import json
import re
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
    ... [irc3.plugins.slack.channels]
    ... slack =
    ...     ${#}irc
    ... """)
    >>> bot = IrcBot(**config)

.. note::

    Be sure to invite the bot in slack to the channels it should be bridging

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
        self.config = self.bot.config.get(__name__, {})
        self.channels = self.bot.config.get(
            '{0}.channels'.format(__name__), {}
        )
        self.clean_channels()  # remove has values from channels
        autojoins = set().union(*self.channels.values())
        self.bot.log.debug('Adding to autojoins list: {autojoins}')
        self.bot.config.setdefault('autojoins', []).extend(autojoins)
        self.slack_channels = {}
        self.slack_users = {}
        if 'token' not in self.config:
            self.bot.log.warning('No slack token is set.')

    def clean_channels(self):
        self.channels.pop('#', None)
        self.channels.pop('hash', None)

    async def api_call(self, method, data=None):
        """Slack API call."""
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData(data or {})
            form.add_field('token', self.config['token'])
            async with session.post(
                'https://slack.com/api/{0}'.format(method), data=form
                    ) as response:
                if response.status != 200:
                    raise Exception(
                        '{0} with {1} failed.'.format(method, data)
                    )
                return await response.json()

    def server_ready(self):
        irc3.asyncio.ensure_future(self.connect())
        self.bot.log.debug('Listening to Slack')

    def parse_text(self, message):

        def getChannelById(matchobj):
            return matchobj.group('readable') or '#{0}'.format(
                self.slack_channels[matchobj.group('channelId')]['name']
            )

        def getUserById(matchobj):
            return matchobj.group('readable') or '@{0}'.format(
                self.slack_users[matchobj.group('userId')]
            )

        def getEmoji(matchobj):
            emoji = matchobj.group('emoji')
            return EMOJIS.get(emoji, emoji)

        matches = [
            (r'\n|\r\n|\r', ''),
            (r'<!channel>', '@channel'),
            (r'<!group>', '@group'),
            (r'<!everyone>', '@everyone'),
            (r'<#(?P<channelId>C\w+)\|?(?P<readable>\w+)?>', getChannelById),
            (r'<@(?P<userId>U\w+)\|?(?P<readable>\w+)?>', getUserById),
            (r':(?P<emoji>\w+):', getEmoji),
            (r'<.+?\|(.+?)>', r'\g<0>'),
            (r'&lt', '<'),
            (r'&gt', '>'),
            (r'&amp', '&'),
        ]
        for match in matches:
            message = re.sub(*match, string=message)
        return message

    async def connect(self):
        channels = await self.api_call('channels.list')
        groups = await self.api_call('groups.list')
        for channel in channels.get('channels', []):
            self.slack_channels[channel['id']] = channel
            if channel['name'] in self.channels:
                self.channels[channel['id']] = self.channels.pop(
                    channel['name']
                )
        for channel in groups.get('groups', []):
            self.slack_channels[channel['id']] = channel
            if channel['name'] in self.channels:
                self.channels[channel['id']] = self.channels.pop(
                    channel['name']
                )
        users = await self.api_call('users.list')
        for user in users['members']:
            self.slack_users[user['id']] = user['name']
        rtm = await self.api_call('rtm.start')
        if not rtm['ok']:
            raise Exception('Error connecting to RTM')
        while True:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(rtm['url']) as ws:
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await self._handle_message(json.loads(msg.data))
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break

    async def _handle_message(self, msg):
        if msg['type'] == 'message' and msg.get('subtype') != 'bot_message':
            self.bot.log.debug(
                'Message to irc: {0}'.format(msg)
            )
            user = await self.api_call(
                'users.info',
                {'user': msg['user']}
            )
            for channel in self.channels.get(msg['channel'], []):
                await self.bot.privmsg(
                    channel,
                    '<{0}> {1}'.format(
                        user['user']['name'],
                        self.parse_text(msg['text'])
                    )
                )

    @irc3.event(r'^(@(?P<tags>\S+) )?:'
                r'(?P<nick>\S+)!(?P<username>\S+)@(?P<hostmask>\S+) '
                r'(?P<event>(PRIVMSG|NOTICE)) '
                r'(?P<target>\S+) :(?P<data>.*)$')
    def on_message(self, target=None, nick=None, data=None, **kwargs):
        self.bot.log.debug(
            'Match Data: {target} {nick} {data} {kwargs}'.format(**locals())
        )
        irc3.asyncio.ensure_future(self.forward_message(target, nick, data))

    async def forward_message(self, target, nick, data):
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
