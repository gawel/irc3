# -*- coding: utf-8 -*-
import os
import codecs
from setuptools import setup
from setuptools import find_packages

version = '1.1.0'

install_requires = ['venusian>=1.0', 'docopt']
test_requires = [
    'pytest-asyncio',
    'pytest-aiohttp',
    'feedparser',
    'requests',
    'pysocks',
    'twitter',
    'aiocron',
    'redis',
    'pytest',
    'irc3-plugins-test',
]


def read(*rnames):
    filename = os.path.join(os.path.dirname(__file__), *rnames)
    with codecs.open(filename, encoding='utf8') as fd:
        return fd.read()


setup(
    name='irc3',
    version=version,
    description=(
        "plugable irc client library based on asyncio "
        "with DCC and SASL support"
    ),
    long_description=read('README.rst'),
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'Development Status :: 5 - Production/Stable',
    ],
    keywords='irc dcc asyncio',
    author='Gael Pasgrimaud',
    author_email='gael@gawel.org',
    url='https://github.com/gawel/irc3/',
    license='MIT',
    packages=find_packages(exclude=['docs', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=test_requires,
    setup_requires=["pytest-runner"],
    extras_require={
        'test': test_requires,
        'web': ['aiohttp'],
    },
    entry_points='''
    [console_scripts]
    irc3 = irc3:run
    irc3d = irc3d:run
    ''',
)
