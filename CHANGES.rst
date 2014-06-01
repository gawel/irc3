0.4.11 (2014-06-01)
===================

- Fixed #9: The ``command`` plugin uses ``cmd``, not ``cmdchar``.

- Fixed #10. Store server config. Use STATUSMSG config if any in ``userlist``

- ``userlist`` plugin now also store user modes per channel.

- Rename ``add_event`` to ``attach_events`` and added ``detach_events``. This
  allow to add/remove events on the fly.

- The autojoin plugin now detach motd related events after triggering one of
  them.

- Fix compatibility with trollius 0.3


0.4.10 (2014-05-21)
===================

- Fixed #5: autojoin on no motd

- allow to show date/times in console log


0.4.9 (2014-05-08)
==================

- Allow to trigger event on output with ``event(iotype='out')``

- Add a channel logger plugin

- autojoins is now a separate plugin

- userlist plugin take care of kicks

- social plugin is now officially supported and tested


0.4.7 (2014-04-03)
==================

- IrcString use unicode with py2


0.4.6 (2014-03-11)
==================

- Bug fix. The cron need a loop sooner as possible.


0.4.5 (2014-02-25)
==================

- Bug fix. An event was run twice if more than one where using the same regexp


0.4.4 (2014-02-15)
==================

- Add cron plugin

- Improve the command plugin. Fix some security issue.

- Add ``--help-page`` option to generate commands help pages


0.4.3 (2014-01-10)
==================

- Fix a bug on connection_lost.

- Send realname in USER command instead of nickname


0.4.2 (2014-01-09)
==================

- python2.7 support.

- add some plugins (ctcp, uptime, feeds, search)

- add some examples/ (twitter, asterisk)

- improve some internals

0.4.1 (2013-12-30)
==================

- Depends on venusian 1.0a8


0.1 (2013-11-30)
================

- Initial release
