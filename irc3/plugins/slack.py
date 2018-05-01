import irc3
import irc3.plugins.cron
import json
import re
__doc__ = '''
==========================================
:mod:`irc3.plugins.slack` Slack plugin
==========================================

Introduce a slack/irc interface to bridge messages between slack and irc.

Install aiohttp and aiocron::

    $ pip install aiohttp aiocron

.. note::

    aiocron is used for refreshing the user and channel list

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

    requires = ['irc3.plugins.cron']

    def __init__(self, bot):
        self.bot = bot
        self.client = irc3.utils.maybedotted('aiohttp.ClientSession')
        self.formdata = irc3.utils.maybedotted('aiohttp.FormData')
        self.msgtype = irc3.utils.maybedotted('aiohttp.WSMsgType')
        self.client_response_error = irc3.utils.maybedotted(
            'aiohttp.client_exceptions.ClientResponseError'
        )
        self.config = self.bot.config.get(__name__, {})
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
        self.bot.create_task(self.connect())

    def parse_text(self, message):
        for match in self.matches:
            message = re.sub(*match, string=message)
        return message

    @irc3.plugins.cron.cron('* * * * 0')
    async def get_users_and_channels(self):
        self.slack_channels = {}
        self.slack_users = {}
        await self.get_channels('channels')
        await self.get_channels('groups')
        await self.get_users()

    async def connect(self):
        rtm = await self.api_call('rtm.start')
        if not rtm['ok']:
            raise ConnectionError('Error connecting to RTM')
        await self.get_users_and_channels()
        try:
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
        except self.client_response_error as exc:
            self.bot.log.exception(exc)
            self.bot.create_task(self.connect())

    async def get_channels(self, what='channels'):
        self.bot.log.debug('Getting Slack %s', what)
        cursor = None
        payload = {'limit': 500}
        while True:
            if cursor:
                payload['cursor'] = cursor
            channels = await self.api_call(
                '{0}.list'.format(what),
                data=payload,
            )
            for channel in channels.get(what, []):
                self.slack_channels[channel['id']] = channel
                if channel['name'] in self.channels:
                    self.channels[channel['id']] = self.channels.pop(
                        channel['name']
                    )
            cursor = channels.get(
                'response_metadata', {}
            ).get('next_cursor', None)
            if not cursor:
                break

    async def get_users(self):
        self.bot.log.debug('Getting Slack users')
        cursor = None
        payload = {'limit': 500}
        while True:
            if cursor:
                payload['cursor'] = cursor
            users = await self.api_call(
                'users.list',
                data=payload,
            )
            for user in users['members']:
                self.slack_users[user['id']] = user['name']
            cursor = users.get(
                'response_metadata', {}
            ).get('next_cursor', None)
            if not cursor:
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
