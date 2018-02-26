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


class SlackException(Exception):
    pass


@irc3.plugin
class Slack:

    def __init__(self, bot):
        self.bot = bot
        self.client = irc3.utils.maybedotted('aiohttp.ClientSession')
        self.formdata = irc3.utils.maybedotted('aiohttp.FormData')
        self.msgtype = irc3.utils.maybedotted('aiohttp.WSMsgType')
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
            (r'<.+?\|(.+?)>', r'\g<0>'),
            (r'&lt', '<'),
            (r'&gt', '>'),
            (r'&amp', '&'),
        ]
        if 'token' not in self.config:
            self.bot.log.warning('No slack token is set.')

    def get_channel_by_id(self, matchobj):
        return matchobj.group('readable') or '#{0}'.format(
            self.slack_channels[matchobj.group('channelId')]['name']
        )

    def get_user_by_id(self, matchobj):
        return matchobj.group('readable') or '@{0}'.format(
            self.slack_users[matchobj.group('userId')]
        )

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
                if response.status != 200:
                    raise Exception(
                        '{0} with {1} failed.'.format(method, data)
                    )
                return await response.json()

    def server_ready(self):
        self.bot.create_task(self.connect())

    def parse_text(self, message):
        for match in self.matches:
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
            raise SlackException('Error connecting to RTM')
        while True:
            async with self.client(loop=self.bot.loop) as session:
                async with session.ws_connect(rtm['url']) as ws:
                    self.bot.log.debug('Listening to Slack')
                    async for msg in ws:
                        if msg.type == self.msgtype.TEXT:
                            data = json.loads(msg.data)
                            if data['type'] == 'message':
                                await self._handle_messages(data)
                        elif msg.type == self.msgtype.CLOSED:
                            break
                        elif msg.type == self.msgtype.ERROR:
                            break

    async def _handle_messages(self, msg):
        self.bot.log.debug(
            'Message to irc: {0}'.format(msg)
        )
        user = None
        if 'user' in msg:
            user = await self.api_call(
                'users.info',
                {'user': msg['user']}
            )
        func = getattr(
            self,
            '_handle_{0}'.format(msg.get('subtype', 'default')),
            None
        )
        if func is not None:
            await func(msg, user=user)

    async def _handle_default(self, msg, user, **kwargs):
        for channel in self.channels.get(msg['channel'], []):
            await self.bot.privmsg(
                channel,
                '<{0}> {1}'.format(
                    user['user']['name'],
                    self.parse_text(msg['text'])
                )
            )

    async def _handle_me_message(self, msg, user, **kwargs):
        for channel in self.channels.get(msg['channel'], []):
            await self.bot.action(
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
