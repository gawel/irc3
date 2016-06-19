from irc3.testing import BotTestCase, patch


class TestAutoCommand(BotTestCase):

    config = dict(includes=['irc3.plugins.autocommand'])

    @patch("irc3.asyncio.sleep")
    def test_autocommand(self, sleep):
        def new_async(coro, *args, **kw):
            for res in coro:
                pass  # do nothing

        with patch('irc3.asyncio.async', new_async):
            # sleep typed in mixed case to test that work with different cases
            bot = self.callFTU(commands=['AUTH user pass', '/slEep  3',
                                         'MODE {nick} +x'])
            bot.notify('connection_made')
            bot.dispatch(':host.freenode.net 376 irc3 :End of /MOTD command.')
            self.assertSent(['AUTH user pass', 'MODE irc3 +x'])
            sleep.assert_called_once_with(3, loop=bot.loop)
            # test bad arguments too
            bot2 = self.callFTU(commands=[None, '/sleep 3.4.5', '/sleep bad',
                                          'TEST SENT'])
            bot2.notify('connection_made')
            bot2.dispatch(':host.freenode.net 376 irc3 :End of /MOTD command.')
            self.assertSent(['TEST SENT'])
