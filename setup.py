# -*- coding: utf-8 -*-
import os
import sys
import codecs
from setuptools import setup
from setuptools import find_packages

version = '0.6.0'

install_requires = ['venusian>=1.0a8', 'docopt']
test_requires = [
    'coverage',
    'feedparser', 'requests',
    'twitter',
    'python-dateutil',
    'croniter',
    'redis',
]

py_ver = sys.version_info[:2]
if py_ver < (3, 0):
    install_requires.extend([
        'trollius',
        'futures',
        'configparser',
    ])
    test_requires.extend(['mock'])
elif py_ver < (3, 3):
    install_requires.append('trollius')
    test_requires.append('mock')
elif py_ver < (3, 4):
    install_requires.append('asyncio')


def read(*rnames):
    filename = os.path.join(os.path.dirname(__file__), *rnames)
    with codecs.open(filename, encoding='utf8') as fd:
        return fd.read()


setup(
    name='irc3',
    version=version,
    description="plugable irc client library based on asyncio",
    long_description=read('README.rst'),
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='irc asyncio tulip',
    author='Gael Pasgrimaud',
    author_email='gael@gawel.org',
    url='https://github.com/gawel/irc3/',
    license='MIT',
    packages=find_packages(exclude=['docs', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'test': test_requires,
    },
    entry_points='''
    [console_scripts]
    irc3 = irc3:run
    irc3d = irc3d:run
    ''',
)
