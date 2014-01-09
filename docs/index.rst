.. irc3 documentation master file, created by
   sphinx-quickstart on Mon Nov 25 01:03:01 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to irc3's documentation!
================================

plugable irc client based on python's `asyncio
<http://docs.python.org/3.4/library/asyncio.html>`_.

Require python 2.7, 3.2+

Source: https://github.com/gawel/irc3/

Docs: https://irc3.readthedocs.org/

Irc: irc://irc.freenode.net/irc3 (`www
<https://kiwiirc.com/client/irc.freenode.net/?nick=irc3|?&theme=basic#irc3>`_)

Installation
==============

Using pip::

    $ pip install irc3

Usage
=====

Here is a simple bot:

.. literalinclude:: ../examples/mybot.py

You can also use a config file as an alternative:

.. literalinclude:: ../examples/bot.ini
   :language: ini

Then run:

.. code-block:: sh

    $ irc3 -h
    $ irc3 bot.ini

See more examples here: https://github.com/gawel/irc3/tree/master/examples

Contents
========

.. toctree::
   :maxdepth: 2
   :glob:

   dec
   utils
   rfc
   plugins/*



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

