Contribute
==========

First, if you want to add a cool plugin, consider submit a pull request to the
`irc3_plugins <https://github.com/gawel/irc3_plugins>`_ instead of irc3 itself.


Feel free to clone the project on `GitHub <https://github.com/gawel/irc3>`_.

To test your change you can run irc3 in debug mode using::

    $ irc3 --debug path-to-your-conf.ini

Once you made a change, try to add a test for your feature/fix. At least assume
that you have'nt broke anything by running tox::

    $ tox
    ...
    py27: commands succeeded
    py32: commands succeeded
    py33: commands succeeded
    py34: commands succeeded
    flake8: commands succeeded
    docs: commands succeeded
    congratulations :)

 You can run tests for a specific version::

    $ tox -e py34

The `irc3.rfc` module is auto generated from `irc3/rfc1459.txt`. If you want to
hack this file, you need to hack the parser in `irc3/_parse_rfc.py` (warning,
it's ugly)

You can regenerate the module and docs by running::

    $ tox -e build

You can also build the docs with::

    $ tox -e docs

And check the result::

    $ firefox .tox/docs/tmp/html/index.html

The project uses ``setuptools``, you can test-install it using `pip`:

    $ pip install .
    $ irc3 -h
