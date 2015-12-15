# -*- coding: utf-8 -*-
import os
import sys
__doc__ = """
Usage: python -m irc3.template <nickname>
"""

dirname = os.path.dirname(__file__)


def get_template(filename, **kwargs):
    with open(os.path.join(dirname, filename)) as fd:
        data = fd.read()
        data = data.format(**kwargs)
    return data


def main(nick=None, user=None, dest=None):
    if nick is None:  # pragma: no cover
        try:
            nick = sys.argv[1]
        except IndexError:
            print(__doc__)
            sys.exit(-1)
    dest = dest or os.getcwd()
    user = user or os.environ.get('USER', 'mynick')
    config = dict(nick=nick, user=user, hash='${hash}')
    data = get_template('config.ini', **config)
    with open(os.path.join(dest, 'config.ini'), 'w') as fd:
        fd.write(data)

    data = get_template('plugin.py', **config)
    filename = os.path.join(dest, '{nick}_plugin.py'.format(**config))
    with open(filename, 'w') as fd:
        fd.write(data)

if __name__ == '__main__':
    main()
