import asyncio
from irc3.testing import BotTestCase, patch
from irc3.plugins.autocommand import AutoCommand, SleepCommand


async def mock(*args, **kwargs):
    pass


class TestAutoCommand(BotTestCase):

    config = dict(includes=['irc3.plugins.autocommand'])

    def test_autocommand(self):
        loop = asyncio.get_event_loop()

        # sleep typed in mixed case to test that work with different cases
        bot = self.callFTU(autocommands=['AUTH user pass', '/slEep  3',
                                         'MODE {nick} +x'])
        with patch('irc3.plugins.autocommand.SleepCommand.execute', mock):
            plugin = bot.get_plugin(AutoCommand)
            loop.run_until_complete(plugin.execute_commands())
            self.assertSent(['AUTH user pass', 'MODE irc3 +x'])

            with self.assertRaises(ValueError):
                # test bad arguments too
                self.callFTU(autocommands=[
                    None, '/sleep 3.4.5', '/sleep bad', 'TEST SENT'])

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
