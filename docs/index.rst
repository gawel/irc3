.. include:: ../README.rst

Installation
==============

Using pip::

    $ pip install irc3

Quick start
===========

irc3 provides a basic template to help you to quickly test a bot.
Here is how to create a bot named ``mybot``.

Create a new directory and cd to it:

.. code-block:: sh

    $ mkdir mybot
    $ cd mybot

Then use the template:

.. code-block:: sh

    $ python -m irc3.template mybot

This will create an almost ready to use ``config.ini`` file and a simple
plugin named ``mybot_plugin.py`` that says «Hi» when the bot or someone else joins a
channel and includes an ``echo`` command.

Here is what the config file will looks like:

.. literalinclude:: ../examples/config.ini
   :language: ini

And here is the plugin:

.. literalinclude:: ../examples/mybot_plugin.py

Have a look at those file and edit the config file for your needs.
You may have to edit:

- the autojoin channel

- your irc mask in the ``irc3.plugins.command.mask`` section

Once you're done with editing, run:

.. code-block:: sh

    $ irc3 config.ini

Check the help of the ``irc3`` command.

.. code-block:: sh

    $ irc3 -h

If you're enjoying it, you can check for more detailed docs below. And some
more examples here: https://github.com/gawel/irc3/tree/master/examples

Documentation
=============

.. toctree::
   :maxdepth: 2
   :glob:

   dec
   utils
   rfc
   dcc
   reloadable
   plugins/*
   hack



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

