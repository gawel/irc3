.. include:: ../README.rst

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

