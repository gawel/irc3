import sys
import getpass
from irc3d import IrcServer


def main():  # pragma: no cover
    args = sys.argv[1:]
    host = '127.0.0.1'
    port = 6667
    if args:
        hp = args.pop(0)
        if ':' in hp:
            host, port = hp.split(':')
        else:
            port = hp
    user = getpass.getuser()
    config = dict(
        servername='test_server',
        host=host,
        port=int(port),
        raw=True,
        opers={user: user},
        includes=['irc3d.plugins.core'],
    )
    print((
        'Starting irc3d test server on {0}:{1} with {2}/{2} as IrcOp'
    ).format(host, port, user))
    server = IrcServer.from_config(config)
    try:
        server.run()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
