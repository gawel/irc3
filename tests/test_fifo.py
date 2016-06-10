from irc3.testing import BotTestCase, MagicMock
from irc3.plugins.fifo import Fifo


class TestFifo(BotTestCase):

    config = {
        "includes": ['irc3.plugins.fifo'],
        "irc3.plugins.fifo": {"runpath": "/tmp/run/irc3"}
    }

    def test_fifo_fake_event_loop(self):
        bot = self.callFTU()
        plugin = bot.get_plugin(Fifo)
        plugin.loop = MagicMock()
        bot.test(':irc3!user@host JOIN #channel')
        channel_fd = plugin.fifos["#channel"]

        with open("/tmp/run/irc3/channel", "wb", 0) as f:
            f.write(b"test1\n")
            plugin.watch_fd(channel_fd, "#chanel")
            self.assertSent(['PRIVMSG #chanel :test1'])

            f.write(b"test2\r\n")
            plugin.watch_fd(channel_fd, "#chanel")
            self.assertSent(['PRIVMSG #chanel :test2'])

            f.write(b"test3\r\ntest4\n")
            plugin.watch_fd(channel_fd, "#chanel")
            self.assertSent(['PRIVMSG #chanel :test3',
                             'PRIVMSG #chanel :test4'])

            for char in b"test5\n":
                f.write(bytes([char]))
                plugin.watch_fd(channel_fd, "#chanel")

            self.assertSent(['PRIVMSG #chanel :test5'])
