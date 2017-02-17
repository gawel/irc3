# -*- coding: utf-8 -*-
import socks
import irc3


def sock_factory(bot, host, port):
    sock = socks.socksocket()
    sock.set_proxy(socks.SOCKS5, "localhost", 6969)
    sock.connect((host, 6667))
    return sock


def main():
    bot = irc3.IrcBot.from_argv(sock_factory=sock_factory)
    bot.run()


if __name__ == '__main__':
    main()
