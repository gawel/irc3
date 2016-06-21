from irc3.testing import BotTestCase, patch
from irc3.plugins.autocommand import AutoCommand, SleepCommand


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
            bot.dispatch(':node.net 376 irc3 :End of /MOTD command.')
            self.assertSent(['AUTH user pass', 'MODE irc3 +x'])
            sleep.assert_called_once_with(3, loop=bot.loop)

            with self.assertRaises(ValueError):
                # test bad arguments too
                bot2 = self.callFTU(commands=[
                        None, '/sleep 3.4.5', '/sleep bad', 'TEST SENT'])
                bot2.notify('connection_made')
                bot2.dispatch(':node.net 376 irc3 '':End of /MOTD command.')
                self.assertSent(['TEST SENT'])

    def test_autocommand_validation(self):
        sleep = AutoCommand.parse_command("/sleeP 3")
        self.assertIsInstance(sleep, SleepCommand)
        self.assertEqual(sleep.time, 3)
        # test unknown command
        with self.assertRaises(ValueError):
            AutoCommand.parse_command("/sleepwhile")

        with self.assertRaises(ValueError):
            AutoCommand.parse_command("/bad")

        # test error on multiple arguments
        with self.assertRaises(ValueError):
            AutoCommand.parse_command("/sleep 3.2 two 3")

        # test sleep without arguments
        with self.assertRaises(ValueError):
            AutoCommand.parse_command("/sleep")

        # test sleep with wrong aruments
        with self.assertRaises(ValueError):
            AutoCommand.parse_command("/sleep bad")

        with self.assertRaises(ValueError):
            AutoCommand.parse_command("/sleep 3.4.5")

        with self.assertRaises(TypeError):
            SleepCommand("bad")
