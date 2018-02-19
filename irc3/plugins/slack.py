import aiohttp
import irc3
import json
import re

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
        self.channels = self.bot.config.get(f'{__name__}.channels', {})
        self.slack_channels = {}
        self.slack_users = {}
        if 'token' not in self.config:
            self.bot.log.warning('No slack token is set.')

    async def api_call(self, method, data=None):
        """Slack API call."""
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData(data or {})
            form.add_field('token', self.config['token'])
            async with session.post('https://slack.com/api/{0}'.format(method), data=form) as response:
                assert 200 == response.status, ('{0} with {1} failed.'.format(method, data))
                return await response.json()

    def server_ready(self):
        irc3.asyncio.ensure_future(self.connect())
        self.bot.log.debug('Listening to Slack')

    def parse_text(self, message):
        def getChannelById(matchobj):
            return matchobj.group('readable') or f"#{self.slack_channels[matchobj.group('channelId')]['name']}"
        def getUserById(matchobj):
            return matchobj.group('readable') or f"@{self.slack_users[matchobj.group('userId')]}"
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
                self.channels[channel['id']] = self.channels.pop(channel['name'])
        for channel in groups.get('groups', []):
            self.slack_channels[channel['id']] = channel
            if channel['name'] in self.channels:
                self.channels[channel['id']] = self.channels.pop(channel['name'])
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
                            message = json.loads(msg.data)
                            if message['type'] == 'message' and message.get('subtype') != 'bot_message':
                                self.bot.log.debug(f'Sending message to irc: {message}')
                                user = await self.api_call('users.info', {'user': message['user']})
                                for channel in self.channels.get(message['channel'], []):
                                    await self.bot.privmsg(channel, f"<{user['user']['name']}> {self.parse_text(message['text'])}")
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break

    @irc3.event(r'^(@(?P<tags>\S+) )?:(?P<nick>\S+)!(?P<username>\S+)@(?P<hostmask>\S+) (?P<event>(PRIVMSG|NOTICE)) '
                r'(?P<target>\S+) :(?P<data>.*)$')
    def on_message(self, target=None, nick=None, data=None, **kwargs):
        self.bot.log.debug(f'Match Data: {target} {nick} {data} {kwargs}')
        irc3.asyncio.ensure_future(self.forward_message(target, nick, data))

    async def forward_message(self, target, nick, data):
        for channel, irc in self.channels.items():
            if target in irc:
                payload = {
                    'channel': channel,
                    'text': data,
                    'as_user': False,
                    'username': nick,
                    'icon_url': f'http://api.adorable.io/avatars/48/{nick}.jpg'
                }
                await self.api_call('chat.postMessage', data=payload)
