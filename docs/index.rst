.. irc3 documentation master file, created by
   sphinx-quickstart on Mon Nov 25 01:03:01 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to irc3's documentation!
================================

irc client based on `asyncio <http://docs.python.org/3.4/library/asyncio.html>`_.

Require python 3.3+

Usage
=====

Installation::

    $ pip install irc3


Here is a simple bot:

.. literalinclude:: ../examples/mybot.py


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

