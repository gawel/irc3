# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.testing import MagicMock
from irc3.testing import patch
from irc3.testing import PY3
from unittest import skipIf


class Event(object):

    def __init__(self, event, **kwargs):
        self.name = event
        self.headers = dict(event=event, **kwargs)

    def get_header(self, name):
        return self.headers[name]

    def update(self, **kwargs):
        self.headers.update(kwargs)
        self.name = self.headers['event']


@skipIf(PY3, 'pyst is not compatible with python3')
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
        patcher = patch('asterisk.manager.Manager.send_action')
        self.send_action = patcher.start()
        self.response = MagicMock()
        self.response.headers = {'Response': 'Success'}
        self.response.get_header.return_value = 'Success'
        self.send_action.return_value = self.response
        self.addCleanup(patcher.stop)

        self.mocks = {}
        for name in ('connect', 'login', 'close'):
            patcher = patch('asterisk.manager.Manager.' + name)
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

        self.assertEqual(plugin.manager, None)
        self.response.get_header.return_value = 'Failure'
        self.assertFalse(plugin.connect())
        self.response.get_header.return_value = 'Success'
        self.assertTrue(plugin.connect())
        self.assertTrue(plugin.manager is not None)

    def test_post_connect_switch_http(self):
        bot, plugin = self.callFTU()
        content = (
            'Response: Follows\r\n'
            'Server Enabled and Bound to 127.0.0.1:8088\n/arawman')
        self.patch_requests(content=content, headers={"response": "Follows"})
        self.response.get_header.return_value = 'Follows'
        self.response.headers = {'response': 'Follows'}
        self.response.data = content
        plugin.post_connect()
        self.assertEqual(plugin.config['use_http'], 'true')

    def test_post_connect_cant_switch_http(self):
        bot, plugin = self.callFTU()
        self.patch_requests(status_code=300)
        self.response.get_header.return_value = 'Follows'
        self.response.headers = {'response': 'Follows'}
        content = 'Server Enabled and Bound to 127.0.0.1:8088\n/arawman'
        self.response.data = content
        plugin.post_connect()
        self.assertEqual(plugin.config['use_http'], 'false')

    def test_update_meetme(self):
        bot, plugin = self.callFTU()
        content = 'No active MeetMe conferences.'
        self.response.get_header.return_value = 'Follows'
        self.response.headers = {'response': 'Follows'}
        self.response.data = content
        plugin.rooms['room'] = {}
        plugin.update_meetme()
        self.assertEqual(len(plugin.rooms), 0)

    def test_update_meetme_fail(self):
        bot, plugin = self.callFTU()
        self.response.get_header.return_value = 'Error'
        self.response.headers = {'response': 'Follows'}
        plugin.rooms['room'] = {}
        plugin.update_meetme()
        self.assertEqual(len(plugin.rooms), 1)

    def test_connect_error(self):
        bot, plugin = self.callFTU()
        self.response.get_header.side_effect = KeyError()
        self.assertFalse(plugin.connect())

    def test_shutdown(self):
        bot, plugin = self.callFTU()
        plugin.connect()
        bot.notify('SIGINT')
        self.assertTrue(self.mocks['close'].called)

        plugin.handle_event(MagicMock(), plugin.manager)
        plugin.handle_shutdown(MagicMock(), plugin.manager)

    def test_send_action_when_disconnected(self):
        bot, plugin = self.callFTU(level=1000)
        success, resp = plugin.send_action({})
        self.assertTrue(success)
        self.assertTrue(plugin.manager is not None)

    def test_send_action_error(self):
        bot, plugin = self.callFTU(level=1000)
        self.assertTrue(plugin.connect())
        self.send_action.side_effect = KeyError()
        success, resp = plugin.send_action({})
        self.assertFalse(success)

    def test_call(self):
        bot, plugin = self.callFTU(level=1000)
        bot.dispatch(':gawel!user@host PRIVMSG nono :!call lukhas')
        self.assertSent(['PRIVMSG gawel :gawel: Call to lukhas done.'])
        bot.dispatch(':gawel!user@host PRIVMSG nono :!call lukhas 061234567')
        self.assertSent(['PRIVMSG gawel :gawel: Call to lukhas done.'])
        bot.dispatch(':gawel!user@host PRIVMSG nono :!call 061234567')
        self.assertSent(['PRIVMSG gawel :gawel: Call to 061234567 done.'])

    def test_invalid_call(self):
        bot, plugin = self.callFTU(level=1000)
        bot.dispatch(':gawel!user@host PRIVMSG nono :!call xx')
        self.assertSent(['PRIVMSG gawel :gawel: Your destination is invalid.'])
        bot.dispatch(':gawel!user@host PRIVMSG nono :!call lukhas xx')
        self.assertSent(['PRIVMSG gawel :gawel: Your caller is invalid.'])

    def test_error_call(self):
        bot, plugin = self.callFTU(level=1000)
        self.assertTrue(plugin.connect())
        self.send_action.side_effect = KeyError()
        bot.dispatch(':gawel!user@host PRIVMSG nono :!call lukhas')
        self.assertSent([
            'PRIVMSG gawel :Sorry an error occured. (KeyError())'])

    def test_error_connection_call(self):
        bot, plugin = self.callFTU(level=1000)
        self.send_action.side_effect = KeyError()
        bot.dispatch(':gawel!user@host PRIVMSG nono :!call lukhas')
        self.assertSent([
            'PRIVMSG gawel :Not able to connect to server. Please retry later'
        ])

    def test_invite(self):
        bot, plugin = self.callFTU(level=1000)
        bot.dispatch(':gawel!user@host PRIVMSG nono :!room invite 4201 lukhas')
        self.assertSent([
            'PRIVMSG gawel :gawel: lukhas has been invited to room 4201.'])

        bot.dispatch(':gawel!user@host PRIVMSG nono :!room invite 4201')
        self.assertSent([
            'PRIVMSG gawel :gawel: You have been invited to room 4201.'])

    def test_invalid_invite(self):
        bot, plugin = self.callFTU(level=1000)
        bot.dispatch(':gawel!user@host PRIVMSG nono :!room invite 4201 xx')
        self.assertSent([
            "PRIVMSG gawel :gawel: I'm not able to resolve xx. Please fix it!"
        ])

    def test_error_invite(self):
        bot, plugin = self.callFTU(level=1000)
        self.send_action.side_effect = KeyError()
        bot.dispatch(':gawel!user@host PRIVMSG nono :!room invite 4210 lukhas')
        self.assertSent([
            'PRIVMSG gawel :Not able to connect to server. Please retry later'
        ])

    def test_status(self):
        bot, plugin = self.callFTU(level=1000)
        self.response.headers = {'SIP-Useragent': 'MyTel',
                                 'Address-IP': 'localhost'}
        bot.dispatch(':gawel!user@host PRIVMSG nono :!voip status')
        self.assertSent([(
            'PRIVMSG gawel :gawel: Your VoIP phone is registered. '
            '(User Agent: MyTel on localhost)'
        )])

        bot.dispatch(':gawel!user@host PRIVMSG nono :!voip status xx')
        self.assertSent(['PRIVMSG gawel :gawel: Your id is invalid.'])

    def test_meetme(self):
        bot, plugin = self.callFTU(level=1000)

        manager = MagicMock()
        event = Event(
            event='MeetmeJoin',
            meetme='4201',
            usernum='1',
            calleridname='gawel',
            calleridnum='4242')
        plugin.handle_meetme(event, manager)

        event.update(usernum='2', calleridname='lukhas')
        plugin.handle_meetme(event, manager)

        event.update(usernum='4', calleridname='external call',
                     calleridnum='42')
        plugin.handle_meetme(event, manager)

        event.update(usernum='3', calleridname='gawel', event='MeetmeLeave')
        plugin.handle_meetme(event, manager)

        self.assertSent([
            ('PRIVMSG #asterirc '
             ':INFO gawel has join room 4201 (total in this room: 1)'),
            ('PRIVMSG #asterirc '
             ':INFO lukhas has join room 4201 (total in this room: 2)'),
            ('PRIVMSG #asterirc '
             ':INFO external call 42 has join room 4201 '
             '(total in this room: 3)'),
            ('PRIVMSG #asterirc '
             ':INFO gawel has leave room 4201 (total in this room: 2)'),
        ])

        bot.dispatch(':gawel!user@host PRIVMSG nono :!room list')
        self.assertSent(['PRIVMSG gawel :Room 4201: lukhas'])
        bot.dispatch(':gawel!user@host PRIVMSG nono :!room list 4201')
        self.assertSent(['PRIVMSG gawel :Room 4201: lukhas'])

        bot.dispatch(':gawel!user@host PRIVMSG nono :!room kick 4201 unknown')
        self.assertSent(['PRIVMSG gawel :No user matching query'])

        bot.dispatch(':gawel!user@host PRIVMSG nono :!room kick 4201 lu')
        self.assertSent(['PRIVMSG gawel :lukhas kicked from 4201.'])

        bot.dispatch(':gawel!user@host PRIVMSG nono :!room kick 4201 42')
        self.assertSent(['PRIVMSG gawel :external call 42 kicked from 4201.'])

        bot.dispatch(':gawel!user@host PRIVMSG nono :!room list')
        self.assertSent(['PRIVMSG gawel :Nobody here.'])

        event.update(event='MeetmeEnd')
        plugin.handle_meetme(event, manager)
        self.assertSent([
            ('PRIVMSG #asterirc '
             ':INFO room 4201 is closed.'),
        ])
