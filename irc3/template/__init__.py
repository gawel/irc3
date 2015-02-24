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


def main(nick=None):
    if nick is None:  # pragma: no cover
        try:
            nick = sys.argv[1]
        except IndexError:
            print(__doc__)
            sys.exit(-1)
    config = dict(nick=nick)
    data = get_template('config.ini', **config)
    with open('config.ini', 'w') as fd:
        fd.write(data)

    data = get_template('plugin.py', **config)
    with open('{nick}_plugin.py'.format(**config), 'w') as fd:
        fd.write(data)

if __name__ == '__main__':
    main()
