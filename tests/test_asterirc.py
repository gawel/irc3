# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.testing import MagicMock
from irc3.testing import patch
from collections import defaultdict
from panoramisk import Message


class Event(Message):

    def __init__(self, event, **kwargs):
        self.name = event
        self.headers = dict(event=event, **kwargs)

    def __getitem__(self, name):
        return self.headers[name]

    def update(self, **kwargs):
        self.headers.update(kwargs)
        self.name = self.headers['event']


class TestAsterirc(BotTestCase):

    config = dict(
        nick='nono',
        includes=['asterirc'],
        asterisk=dict(username='username', secret='secret',
                      resolver='asterirc.default_resolver',
                      channel='#asterirc'),
    )

    def setUp(self):
        self.patch_asyncio()
        patcher = patch('panoramisk.Manager.send_action_via_http')
        self.send_action = patcher.start()
        self.response = Message(
            'response', '', headers={'Response': 'Success'})
        self.send_action.return_value = self.response
        self.addCleanup(patcher.stop)

        self.mocks = {}
        for name in ('connect', 'close'):
            patcher = patch('panoramisk.Manager.' + name)
            self.mocks[name] = patcher.start()
            self.addCleanup(patcher.stop)

    def callFTU(self, level=1000, **kwargs):
        bot = super(TestAsterirc, self).callFTU()
        plugin = bot.asterirc
        plugin.config.update(**kwargs)
        plugin.log.setLevel(level)
        return bot, plugin

    def test_connect(self):
        bot, plugin = self.callFTU(debug=True)
        bot.notify('connection_made')
        self.assertTrue(plugin.connect())
        self.assertTrue(plugin.manager is not None)

    def test_connect_failed(self):
        bot, plugin = self.callFTU(debug=True)
        self.mocks['connect'].side_effect = KeyError()
        self.assertFalse(plugin.connect())

    def test_update_meetme(self):
        bot, plugin = self.callFTU()
        plugin.connect()
        plugin.rooms['room'] = {}
        self.response.headers = {'response': 'Follows'}
        content = 'No active MeetMe conferences.'
        self.response.text = content
        plugin.post_connect()
        self.assertEqual(len(plugin.rooms), 0)

        content = '''
Conf Num       Parties        Marked     Activity  Creation  Locked
4290           0001	      N/A        00:20:33  Static    No
User #: 01  gawel Gael Pasgrimaud      Channel: SIP/gawel
User #: 02  <unknow> External Call 0699999999     Channel: SIP/gawel

--END COMMAND--
'''
        self.response.headers = {'response': 'Follows'}
        self.response.text = content.strip()
        plugin.rooms = defaultdict(dict)
        plugin.update_meetme()
        self.assertEqual(len(plugin.rooms), 1, plugin.rooms)
        self.assertEqual(len(plugin.rooms['4290']), 2, plugin.rooms)

    def test_update_meetme_fail(self):
        bot, plugin = self.callFTU()
        plugin.connect()
        self.response.headers = {'response': 'Follows'}
        plugin.rooms = defaultdict(dict)
        plugin.update_meetme()
        self.assertEqual(len(plugin.rooms), 0)

    def test_shutdown(self):
        bot, plugin = self.callFTU()
        plugin.connect()
        bot.notify('SIGINT')
        self.assertTrue(self.mocks['close'].called)

        event = MagicMock(manager=plugin.manager)

        plugin.handle_event(event, MagicMock())
        plugin.handle_shutdown(event, MagicMock())

    def test_send_action_error(self):
        bot, plugin = self.callFTU(level=1000)
        self.assertTrue(plugin.connect())
        self.send_action.side_effect = KeyError()
        resp = plugin.send_action({})
        self.assertFalse(resp.success)

    def test_call(self):
        bot, plugin = self.callFTU(level=1000)
        plugin.connect()
        bot.dispatch(':gawel!user@host PRIVMSG nono :!call lukhas')
        self.assertSent(['PRIVMSG gawel :gawel: Call to lukhas done.'])
        bot.dispatch(':gawel!user@host PRIVMSG nono :!call lukhas 061234567')
        self.assertSent(['PRIVMSG gawel :gawel: Call to lukhas done.'])
        bot.dispatch(':gawel!user@host PRIVMSG nono :!call 061234567')
        self.assertSent(['PRIVMSG gawel :gawel: Call to 061234567 done.'])

    def test_invalid_call(self):
        bot, plugin = self.callFTU(level=1000)
        plugin.connect()
        bot.dispatch(':gawel!user@host PRIVMSG nono :!call xx')
        self.assertSent(['PRIVMSG gawel :gawel: Your destination is invalid.'])
        bot.dispatch(':gawel!user@host PRIVMSG nono :!call lukhas xx')
        self.assertSent(['PRIVMSG gawel :gawel: Your caller is invalid.'])

    def test_error_call(self):
        bot, plugin = self.callFTU(level=1000)
        plugin.connect()
        self.assertTrue(plugin.connect())
        self.send_action.side_effect = KeyError()
        bot.dispatch(':gawel!user@host PRIVMSG nono :!call lukhas')
        self.assertSent([
            'PRIVMSG gawel :Sorry an error occured. (KeyError())'])

    def test_invite(self):
        bot, plugin = self.callFTU(level=1000)
        plugin.connect()
        bot.dispatch(':gawel!user@host PRIVMSG nono :!room invite 4201 lukhas')
        self.assertSent([
            'PRIVMSG gawel :gawel: lukhas has been invited to room 4201.'])

        bot.dispatch(':gawel!user@host PRIVMSG nono :!room invite 4201')
        self.assertSent([
            'PRIVMSG gawel :gawel: You have been invited to room 4201.'])

    def test_invalid_invite(self):
        bot, plugin = self.callFTU(level=1000)
        plugin.connect()
        bot.dispatch(':gawel!user@host PRIVMSG nono :!room invite 4201 xx')
        self.assertSent([
            "PRIVMSG gawel :gawel: I'm not able to resolve xx. Please fix it!"
        ])

    def test_error_invite(self):
        bot, plugin = self.callFTU(level=1000)
        plugin.connect()
        self.send_action.side_effect = KeyError()
        bot.dispatch(':gawel!user@host PRIVMSG nono :!room invite 4210 lukhas')
        self.assertSent([
            'PRIVMSG gawel :Sorry an error occured. (KeyError())'])

    def test_status(self):
        bot, plugin = self.callFTU(level=1000)
        plugin.connect()
        self.response.headers = {'SIP-Useragent': 'MyTel',
                                 'Address-IP': 'localhost',
                                 'response': 'Follows'}
        bot.dispatch(':gawel!user@host PRIVMSG nono :!asterisk status')
        self.assertSent([(
            'PRIVMSG gawel :gawel: Your VoIP phone is registered. '
            '(User Agent: MyTel on localhost)'
        )])

        bot.dispatch(':gawel!user@host PRIVMSG nono :!asterisk status xx')
        self.assertSent(['PRIVMSG gawel :gawel: Your id is invalid.'])

    def test_meetme(self):
        bot, plugin = self.callFTU(level=1000)
        plugin.connect()

        event = Event(
            event='MeetmeJoin',
            meetme='4201',
            usernum='1',
            calleridname='gawel',
            calleridnum='4242')
        plugin.handle_meetme(event, MagicMock())

        event.update(usernum='2', calleridname='lukhas')
        plugin.handle_meetme(event, MagicMock())

        event.update(usernum='4', calleridname='external call 0699999999')
        plugin.handle_meetme(event, MagicMock())

        event.update(usernum='3', calleridname='gawel', event='MeetmeLeave')
        plugin.handle_meetme(event, MagicMock())

        self.assertSent([
            ('PRIVMSG #asterirc '
             ':INFO gawel has join room 4201 (total in this room: 1)'),
            ('PRIVMSG #asterirc '
             ':INFO lukhas has join room 4201 (total in this room: 2)'),
            ('PRIVMSG #asterirc '
             ':INFO external call 069999 has join room 4201 '
             '(total in this room: 3)'),
            ('PRIVMSG #asterirc '
             ':INFO gawel has leave room 4201 (total in this room: 2)'),
        ])

        bot.dispatch(':gawel!user@host PRIVMSG nono :!room list')
        self.assertSent([
            'PRIVMSG gawel :Room 4201 (2): external call 069999, lukhas'])
        bot.dispatch(':gawel!user@host PRIVMSG nono :!room list 4201')
        self.assertSent([
            'PRIVMSG gawel :Room 4201 (2): external call 069999, lukhas'])

        bot.dispatch(':gawel!user@host PRIVMSG nono :!room kick 4201 unknown')
        self.assertSent(['PRIVMSG gawel :No user matching query'])

        bot.dispatch(':gawel!user@host PRIVMSG nono :!room kick 4201 lu')
        self.assertSent(['PRIVMSG gawel :lukhas kicked from 4201.'])

        bot.dispatch(':gawel!user@host PRIVMSG nono :!room kick 4201 06')
        self.assertSent([
            'PRIVMSG gawel :external call 069999 kicked from 4201.'])

        bot.dispatch(':gawel!user@host PRIVMSG nono :!room list')
        self.assertSent(['PRIVMSG gawel :Nobody here.'])

        event.update(event='MeetmeEnd')
        plugin.handle_meetme(event, MagicMock())
        self.assertSent([
            ('PRIVMSG #asterirc '
             ':INFO room 4201 is closed.'),
        ])
