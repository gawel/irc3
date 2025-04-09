# -*- coding: utf-8 -*-
from unittest import TestCase
from irc3.utils import IrcString
from irc3.utils import maybedotted
from irc3.utils import split_message
from irc3.utils import parse_config_env
from irc3.utils import slugify
from irc3.testing import ini2config
import irc3.plugins


def test_hash():
    config = ini2config('''
[bot]
autojoins =
    ${hash}irc3
    ${hash}${hash}irc3
    ${#}irc3
    ${#}${#}irc3
    ${##}irc3
''')
    assert config['autojoins'] == [
        '#irc3',
        '##irc3',
        '#irc3',
        '##irc3',
        '##irc3',
    ]


def test_config_env():
    config = ini2config('''
[bot]
nickname = bot
''', env={'IRC3_BOT_AUTOJOINS': '#irc3 ##irc3'})
    assert config['autojoins'] == ['#irc3', '##irc3']


class TestUtils(TestCase):

    def test_ircstring(self):
        s = IrcString('nick')
        self.assertTrue(s.is_nick)
        self.assertEqual(s.nick, 'nick')
        self.assertEqual(s.host, None)

        s = IrcString('nick!user@host')
        self.assertTrue(s.is_user)
        self.assertTrue(s.is_nick)
        self.assertEqual(s.nick, 'nick')
        self.assertEqual(s.host, 'user@host')
        self.assertEqual(s.username, 'user')
        self.assertEqual(s.hostname, 'host')

        s = IrcString('#chan')
        self.assertTrue(s.is_channel)
        s = IrcString('&chan')
        self.assertTrue(s.is_channel)

        s = IrcString('*')
        self.assertTrue(s.is_server)

    def test_maybedotted(self):
        self.assertTrue(
            maybedotted('irc3.plugins') is irc3.plugins)
        self.assertTrue(
            maybedotted('irc3.utils.IrcString') is IrcString)
        self.assertTrue(
            maybedotted(IrcString) is IrcString)
        self.assertRaises(LookupError, maybedotted, 'irc3.none.none')
        self.assertRaises(LookupError, maybedotted, 'irc3.none')
        self.assertRaises(LookupError, maybedotted, None)
        self.assertRaises(LookupError, maybedotted, '')

    def test_slugify(self):
        assert slugify('a test file .rst') == 'a-test-file.rst'
        assert slugify('a test/../ file .rst') == 'a-test.file.rst'
        assert slugify(r'C:\\a test\../ file .rst') == 'ca-test.file.rst'


class TestConfig(TestCase):

    def test_config_env(self):
        value = parse_config_env({
            'IRC3_BOT_NICKNAME': 'env_nickname',
            'IRC3_BOT_PASSWORD': 'env_password',

            'IRC3__BOT__SASL_PASSWORD': 'hunter2',
            'IRC3__IRC3__PLUGINS__FOO__BAR_BAZ': 'qux',
        })
        self.assertEqual(value, {
            'bot': {
                'nickname': 'env_nickname',
                'password': 'env_password',

                'sasl_password': 'hunter2',
            },
            'irc3.plugins.foo': {
                'bar_baz': 'qux',
            },
        })


class TestSplit(TestCase):

    def test_split_message(self):
        messages = [
            'allo',
            'allo\t',
            '   allo',
            'alloallo',
            'Qwerty uiop asdfghjkl zxcvbnm',
            '\x1d \x1f',
            # "Hello world!" in Belarusian, Greek, and Japanese.
            'Прывітанне свет!',
            'Γειά σου Κόσμε!',
            'こんにちは 世界',
        ]
        expected = [
            ['allo'],
            ['allo\t'],
            ['   allo'],
            ['alloallo'],
            ['Qwerty', 'uiop', 'asdfghjkl', 'zxcvbnm'],
            ['\x1d \x1f'],
            ['Прыві', 'танне', 'свет!'],
            ['Γειά', 'σου', 'Κόσμε', '!'],
            ['こんに', 'ちは', '世界'],
        ]

        split = [
            list(split_message(msg, 10, 'utf-8'))
            for msg in messages
        ]
        self.assertEqual(split, expected)

    def test_split_message_long(self):
        message = (
            'Harum qui commodi voluptas veritatis provident voluptatem '
            'accusamus. Ut odio porro voluptas. Totam perspiciatis dolorem '
            'maxime beatae sit. Consectetur ducimus qui ut quae. Dolor optio '
            'minima cupiditate ut. Laborum officia ut voluptas est porro '
            'nulla qui.'
        )
        expected = {
            50: [
                # 1
                'Harum qui commodi voluptas veritatis provident',
                # 2
                'voluptatem accusamus. Ut odio porro voluptas.',
                # 3
                'Totam perspiciatis dolorem maxime beatae sit.',
                # 4
                'Consectetur ducimus qui ut quae. Dolor optio',
                # 5
                'minima cupiditate ut. Laborum officia ut voluptas',
                # 6
                'est porro nulla qui.',
            ],
            100: [
                # 1
                'Harum qui commodi voluptas veritatis provident voluptatem '
                'accusamus. Ut odio porro voluptas. Totam',
                # 2
                'perspiciatis dolorem maxime beatae sit. Consectetur ducimus '
                'qui ut quae. Dolor optio minima',
                # 3
                'cupiditate ut. Laborum officia ut voluptas est porro nulla '
                'qui.',
            ],
            150: [
                # 1
                'Harum qui commodi voluptas veritatis provident voluptatem '
                'accusamus. Ut odio porro voluptas. Totam perspiciatis '
                'dolorem maxime beatae sit.',
                # 2
                'Consectetur ducimus qui ut quae. Dolor optio minima '
                'cupiditate ut. Laborum officia ut voluptas est porro nulla '
                'qui.',
            ],
            200: [
                # 1
                'Harum qui commodi voluptas veritatis provident voluptatem '
                'accusamus. Ut odio porro voluptas. Totam perspiciatis '
                'dolorem maxime beatae sit. Consectetur ducimus qui ut quae. '
                'Dolor optio minima',
                # 2
                'cupiditate ut. Laborum officia ut voluptas est porro nulla '
                'qui.',
            ],
            300: [message],
        }

        for max_bytes in expected.keys():
            split = list(
                split_message(message, max_bytes, 'utf-8')
            )
            self.assertEqual(split, expected[max_bytes])

    def test_split_message_no_whitespace(self):
        message_len = 100
        message = 'A' * message_len

        def split_lens(max_bytes):
            split = list(
                split_message(message, max_bytes, 'utf-8')
            )
            return len(''.join(split)), len(split)

        result = [
            (max_bytes, *split_lens(max_bytes))
            for max_bytes in [*range(1, 10), *range(10, 110, 10)]
        ]
        expected = [
            (1, 100, 100),
            (2, 100, 50),
            (3, 100, 34),
            (4, 100, 25),
            (5, 100, 20),
            (6, 100, 17),
            (7, 100, 15),
            (8, 100, 13),
            (9, 100, 12),
            (10, 100, 10),
            (20, 100, 5),
            (30, 100, 4),
            (40, 100, 3),
            (50, 100, 2),
            (60, 100, 2),
            (70, 100, 2),
            (80, 100, 2),
            (90, 100, 2),
            (100, 100, 1),
        ]
        self.assertEqual(result, expected)

    def test_split_message_byte_max_bytes_too_small(self):
        message = 'こんにちは'

        for max_bytes in (1, 2):
            with self.assertRaisesRegex(ValueError, f'{max_bytes=}'):
                list(split_message(message, max_bytes, 'utf-8'))
