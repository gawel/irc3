========================
:mod:`irc3.rfc` RFC1459
========================

Replies (REPL)
==============

259 - RPL_ADMINEMAIL
--------------------

Match ``^:(?P<srv>\S+) 259 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ADMINEMAIL)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

257 - RPL_ADMINLOC1
-------------------

Match ``^:(?P<srv>\S+) 257 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ADMINLOC1)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

258 - RPL_ADMINLOC2
-------------------

Match ``^:(?P<srv>\S+) 258 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ADMINLOC2)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

256 - RPL_ADMINME
-----------------

Match ``^:(?P<srv>\S+) 256 (?P<me>\S+) (?P<server>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ADMINME)
    def myevent(bot, srv=None, me=None, server=None, data=None):
        # do something

301 - RPL_AWAY
--------------

Match ``^:(?P<srv>\S+) 301 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_AWAY)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

367 - RPL_BANLIST
-----------------

Match ``^:(?P<srv>\S+) 367 (?P<me>\S+) (?P<channel>\S+) (?P<banid>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_BANLIST)
    def myevent(bot, srv=None, me=None, channel=None, banid=None):
        # do something

324 - RPL_CHANNELMODEIS
-----------------------

Match ``^:(?P<srv>\S+) 324 (?P<me>\S+) (?P<channel>\S+) (?P<mode>\S+) (?P<mode_params>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_CHANNELMODEIS)
    def myevent(bot, srv=None, me=None, channel=None, mode=None, mode_params=None):
        # do something

368 - RPL_ENDOFBANLIST
----------------------

Match ``^:(?P<srv>\S+) 368 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFBANLIST)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

374 - RPL_ENDOFINFO
-------------------

Match ``^:(?P<srv>\S+) 374 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFINFO)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

365 - RPL_ENDOFLINKS
--------------------

Match ``^:(?P<srv>\S+) 365 (?P<me>\S+) (?P<mask>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFLINKS)
    def myevent(bot, srv=None, me=None, mask=None, data=None):
        # do something

376 - RPL_ENDOFMOTD
-------------------

Match ``^:(?P<srv>\S+) 376 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFMOTD)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

366 - RPL_ENDOFNAMES
--------------------

Match ``^:(?P<srv>\S+) 366 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFNAMES)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

219 - RPL_ENDOFSTATS
--------------------

Match ``^:(?P<srv>\S+) 219 (?P<me>\S+) (?P<stats_letter>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFSTATS)
    def myevent(bot, srv=None, me=None, stats_letter=None, data=None):
        # do something

394 - RPL_ENDOFUSERS
--------------------

Match ``^:(?P<srv>\S+) 394 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFUSERS)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

315 - RPL_ENDOFWHO
------------------

Match ``^:(?P<srv>\S+) 315 (?P<me>\S+) (?P<name>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFWHO)
    def myevent(bot, srv=None, me=None, name=None, data=None):
        # do something

318 - RPL_ENDOFWHOIS
--------------------

Match ``^:(?P<srv>\S+) 318 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFWHOIS)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

369 - RPL_ENDOFWHOWAS
---------------------

Match ``^:(?P<srv>\S+) 369 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFWHOWAS)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

371 - RPL_INFO
--------------

Match ``^:(?P<srv>\S+) 371 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_INFO)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

341 - RPL_INVITING
------------------

Match ``^:(?P<srv>\S+) 341 (?P<me>\S+) (?P<channel>\S+) (?P<nick>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_INVITING)
    def myevent(bot, srv=None, me=None, channel=None, nick=None):
        # do something

303 - RPL_ISON
--------------

Match ``^:(?P<srv>\S+) 303 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ISON)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

364 - RPL_LINKS
---------------

Match ``^:(?P<srv>\S+) 364 (?P<me>\S+) (?P<mask>\S+) (?P<server>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LINKS)
    def myevent(bot, srv=None, me=None, mask=None, server=None, data=None):
        # do something

322 - RPL_LIST
--------------

Match ``^:(?P<srv>\S+) 322 (?P<me>\S+) (?P<channel>\S+) (?P<visible>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LIST)
    def myevent(bot, srv=None, me=None, channel=None, visible=None, data=None):
        # do something

323 - RPL_LISTEND
-----------------

Match ``^:(?P<srv>\S+) 323 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LISTEND)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

321 - RPL_LISTSTART
-------------------

Match ``^:(?P<srv>\S+) 321 (?P<me>\S+) Channel :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LISTSTART)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

254 - RPL_LUSERCHANNELS
-----------------------

Match ``^:(?P<srv>\S+) 254 (?P<me>\S+) (?P<integer>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LUSERCHANNELS)
    def myevent(bot, srv=None, me=None, integer=None, data=None):
        # do something

251 - RPL_LUSERCLIENT
---------------------

Match ``^:(?P<srv>\S+) 251 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LUSERCLIENT)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

255 - RPL_LUSERME
-----------------

Match ``^:(?P<srv>\S+) 255 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LUSERME)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

252 - RPL_LUSEROP
-----------------

Match ``^:(?P<srv>\S+) 252 (?P<me>\S+) (?P<integer>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LUSEROP)
    def myevent(bot, srv=None, me=None, integer=None, data=None):
        # do something

253 - RPL_LUSERUNKNOWN
----------------------

Match ``^:(?P<srv>\S+) 253 (?P<me>\S+) (?P<integer>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LUSERUNKNOWN)
    def myevent(bot, srv=None, me=None, integer=None, data=None):
        # do something

372 - RPL_MOTD
--------------

Match ``^:(?P<srv>\S+) 372 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_MOTD)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

375 - RPL_MOTDSTART
-------------------

Match ``^:(?P<srv>\S+) 375 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_MOTDSTART)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

353 - RPL_NAMREPLY
------------------

Match ``^:(?P<srv>\S+) 353 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_NAMREPLY)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

331 - RPL_NOTOPIC
-----------------

Match ``^:(?P<srv>\S+) 331 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_NOTOPIC)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

395 - RPL_NOUSERS
-----------------

Match ``^:(?P<srv>\S+) 395 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_NOUSERS)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

306 - RPL_NOWAWAY
-----------------

Match ``^:(?P<srv>\S+) 306 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_NOWAWAY)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

382 - RPL_REHASHING
-------------------

Match ``^:(?P<srv>\S+) 382 (?P<me>\S+) (?P<config_file>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_REHASHING)
    def myevent(bot, srv=None, me=None, config_file=None, data=None):
        # do something

213 - RPL_STATSCLINE
--------------------

Match ``^:(?P<srv>\S+) 213 (?P<me>\S+) C (?P<host>\S+) * (?P<name>\S+) (?P<port>\S+) (?P<class>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSCLINE)
    def myevent(bot, srv=None, me=None, host=None, name=None, port=None, class=None):
        # do something

212 - RPL_STATSCOMMANDS
-----------------------

Match ``^:(?P<srv>\S+) 212 (?P<me>\S+) (?P<command>\S+) (?P<count>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSCOMMANDS)
    def myevent(bot, srv=None, me=None, command=None, count=None):
        # do something

244 - RPL_STATSHLINE
--------------------

Match ``^:(?P<srv>\S+) 244 (?P<me>\S+) H (?P<hostmask>\S+) * (?P<servername>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSHLINE)
    def myevent(bot, srv=None, me=None, hostmask=None, servername=None):
        # do something

215 - RPL_STATSILINE
--------------------

Match ``^:(?P<srv>\S+) 215 (?P<me>\S+) I (?P<host>\S+) * (?P<host>\S+) (?P<port>\S+) (?P<class>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSILINE)
    def myevent(bot, srv=None, me=None, host=None, host=None, port=None, class=None):
        # do something

216 - RPL_STATSKLINE
--------------------

Match ``^:(?P<srv>\S+) 216 (?P<me>\S+) K (?P<host>\S+) * (?P<username>\S+) (?P<port>\S+) (?P<class>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSKLINE)
    def myevent(bot, srv=None, me=None, host=None, username=None, port=None, class=None):
        # do something

211 - RPL_STATSLINKINFO
-----------------------

Match ``^:(?P<srv>\S+) 211 (?P<me>\S+) (?P<linkname>\S+) (?P<sendq>\S+) (?P<sent_messages>\S+) (?P<received_bytes>\S+) (?P<time_open>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSLINKINFO)
    def myevent(bot, srv=None, me=None, linkname=None, sendq=None, sent_messages=None, received_bytes=None, time_open=None):
        # do something

241 - RPL_STATSLLINE
--------------------

Match ``^:(?P<srv>\S+) 241 (?P<me>\S+) L (?P<hostmask>\S+) * (?P<servername>\S+) (?P<maxdepth>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSLLINE)
    def myevent(bot, srv=None, me=None, hostmask=None, servername=None, maxdepth=None):
        # do something

214 - RPL_STATSNLINE
--------------------

Match ``^:(?P<srv>\S+) 214 (?P<me>\S+) N (?P<host>\S+) * (?P<name>\S+) (?P<port>\S+) (?P<class>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSNLINE)
    def myevent(bot, srv=None, me=None, host=None, name=None, port=None, class=None):
        # do something

243 - RPL_STATSOLINE
--------------------

Match ``^:(?P<srv>\S+) 243 (?P<me>\S+) O (?P<hostmask>\S+) * (?P<name>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSOLINE)
    def myevent(bot, srv=None, me=None, hostmask=None, name=None):
        # do something

242 - RPL_STATSUPTIME
---------------------

Match ``^:(?P<srv>\S+) 242 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSUPTIME)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

218 - RPL_STATSYLINE
--------------------

Match ``^:(?P<srv>\S+) 218 (?P<me>\S+) frequency> (?P<max_sendq>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSYLINE)
    def myevent(bot, srv=None, me=None, max_sendq=None):
        # do something

342 - RPL_SUMMONING
-------------------

Match ``^:(?P<srv>\S+) 342 (?P<me>\S+) (?P<user>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_SUMMONING)
    def myevent(bot, srv=None, me=None, user=None, data=None):
        # do something

391 - RPL_TIME
--------------

Match ``^:(?P<srv>\S+) 391 (?P<me>\S+) (?P<server>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TIME)
    def myevent(bot, srv=None, me=None, server=None, data=None):
        # do something

332 - RPL_TOPIC
---------------

Match ``^:(?P<srv>\S+) 332 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TOPIC)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

201 - RPL_TRACECONNECTING
-------------------------

Match ``^:(?P<srv>\S+) 201 (?P<me>\S+) Try. (?P<class>\S+) (?P<server>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACECONNECTING)
    def myevent(bot, srv=None, me=None, class=None, server=None):
        # do something

202 - RPL_TRACEHANDSHAKE
------------------------

Match ``^:(?P<srv>\S+) 202 (?P<me>\S+) H.S. (?P<class>\S+) (?P<server>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACEHANDSHAKE)
    def myevent(bot, srv=None, me=None, class=None, server=None):
        # do something

200 - RPL_TRACELINK
-------------------

Match ``^:(?P<srv>\S+) 200 (?P<me>\S+) (?P<next_server>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACELINK)
    def myevent(bot, srv=None, me=None, next_server=None):
        # do something

261 - RPL_TRACELOG
------------------

Match ``^:(?P<srv>\S+) 261 (?P<me>\S+) File (?P<logfile>\S+) (?P<debug_level>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACELOG)
    def myevent(bot, srv=None, me=None, logfile=None, debug_level=None):
        # do something

208 - RPL_TRACENEWTYPE
----------------------

Match ``^:(?P<srv>\S+) 208 (?P<me>\S+) (?P<newtype>\S+) 0 (?P<client>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACENEWTYPE)
    def myevent(bot, srv=None, me=None, newtype=None, client=None):
        # do something

204 - RPL_TRACEOPERATOR
-----------------------

Match ``^:(?P<srv>\S+) 204 (?P<me>\S+) Oper (?P<class>\S+) (?P<nick>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACEOPERATOR)
    def myevent(bot, srv=None, me=None, class=None, nick=None):
        # do something

206 - RPL_TRACESERVER
---------------------

Match ``^:(?P<srv>\S+) 206 (?P<me>\S+) (?P<mask>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACESERVER)
    def myevent(bot, srv=None, me=None, mask=None):
        # do something

203 - RPL_TRACEUNKNOWN
----------------------

Match ``^:(?P<srv>\S+) 203 (?P<me>\S+) ???? (?P<class>\S+) [(?P<clientip>\S+)]``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACEUNKNOWN)
    def myevent(bot, srv=None, me=None, class=None, clientip=None):
        # do something

205 - RPL_TRACEUSER
-------------------

Match ``^:(?P<srv>\S+) 205 (?P<me>\S+) User (?P<class>\S+) (?P<nick>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACEUSER)
    def myevent(bot, srv=None, me=None, class=None, nick=None):
        # do something

221 - RPL_UMODEIS
-----------------

Match ``^:(?P<srv>\S+) 221 (?P<me>\S+) (?P<user_mode_string>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_UMODEIS)
    def myevent(bot, srv=None, me=None, user_mode_string=None):
        # do something

305 - RPL_UNAWAY
----------------

Match ``^:(?P<srv>\S+) 305 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_UNAWAY)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

302 - RPL_USERHOST
------------------

Match ``^:(?P<srv>\S+) 302 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_USERHOST)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

393 - RPL_USERS
---------------

Match ``^:(?P<srv>\S+) 393 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_USERS)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

392 - RPL_USERSSTART
--------------------

Match ``^:(?P<srv>\S+) 392 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_USERSSTART)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

351 - RPL_VERSION
-----------------

Match ``^:(?P<srv>\S+) 351 (?P<me>\S+) (?P<version>\S+).(?P<debuglevel>\S+) (?P<server>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_VERSION)
    def myevent(bot, srv=None, me=None, version=None, debuglevel=None, server=None, data=None):
        # do something

319 - RPL_WHOISCHANNELS
-----------------------

Match ``^:(?P<srv>\S+) 319 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_WHOISCHANNELS)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

317 - RPL_WHOISIDLE
-------------------

Match ``^:(?P<srv>\S+) 317 (?P<me>\S+) (?P<nick>\S+) (?P<integer>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_WHOISIDLE)
    def myevent(bot, srv=None, me=None, nick=None, integer=None, data=None):
        # do something

313 - RPL_WHOISOPERATOR
-----------------------

Match ``^:(?P<srv>\S+) 313 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_WHOISOPERATOR)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

312 - RPL_WHOISSERVER
---------------------

Match ``^:(?P<srv>\S+) 312 (?P<me>\S+) (?P<nick>\S+) (?P<server>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_WHOISSERVER)
    def myevent(bot, srv=None, me=None, nick=None, server=None, data=None):
        # do something

311 - RPL_WHOISUSER
-------------------

Match ``^:(?P<srv>\S+) 311 (?P<me>\S+) (?P<nick>\S+) (?P<user>\S+) (?P<host>\S+) * :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_WHOISUSER)
    def myevent(bot, srv=None, me=None, nick=None, user=None, host=None, data=None):
        # do something

352 - RPL_WHOREPLY
------------------

Match ``^:(?P<srv>\S+) 352 (?P<me>\S+) (?P<channel>\S+) (?P<user>\S+) (?P<host>\S+) (?P<server>\S+) (?P<nick>\S+) (?P<modes>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_WHOREPLY)
    def myevent(bot, srv=None, me=None, channel=None, user=None, host=None, server=None, nick=None, modes=None, data=None):
        # do something

314 - RPL_WHOWASUSER
--------------------

Match ``^:(?P<srv>\S+) 314 (?P<me>\S+) (?P<nick>\S+) (?P<user>\S+) (?P<host>\S+) * :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_WHOWASUSER)
    def myevent(bot, srv=None, me=None, nick=None, user=None, host=None, data=None):
        # do something

381 - RPL_YOUREOPER
-------------------

Match ``^:(?P<srv>\S+) 381 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_YOUREOPER)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

Errors (ERR)
============

462 - ERR_ALREADYREGISTRED
--------------------------

Match ``^:(?P<srv>\S+) 462 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_ALREADYREGISTRED)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

475 - ERR_BADCHANNELKEY
-----------------------

Match ``^:(?P<srv>\S+) 475 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_BADCHANNELKEY)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

474 - ERR_BANNEDFROMCHAN
------------------------

Match ``^:(?P<srv>\S+) 474 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_BANNEDFROMCHAN)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

404 - ERR_CANNOTSENDTOCHAN
--------------------------

Match ``^:(?P<srv>\S+) 404 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_CANNOTSENDTOCHAN)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

483 - ERR_CANTKILLSERVER
------------------------

Match ``^:(?P<srv>\S+) 483 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_CANTKILLSERVER)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

471 - ERR_CHANNELISFULL
-----------------------

Match ``^:(?P<srv>\S+) 471 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_CHANNELISFULL)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

482 - ERR_CHANOPRIVSNEEDED
--------------------------

Match ``^:(?P<srv>\S+) 482 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_CHANOPRIVSNEEDED)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

432 - ERR_ERRONEUSNICKNAME
--------------------------

Match ``^:(?P<srv>\S+) 432 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_ERRONEUSNICKNAME)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

473 - ERR_INVITEONLYCHAN
------------------------

Match ``^:(?P<srv>\S+) 473 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_INVITEONLYCHAN)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

467 - ERR_KEYSET
----------------

Match ``^:(?P<srv>\S+) 467 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_KEYSET)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

461 - ERR_NEEDMOREPARAMS
------------------------

Match ``^:(?P<srv>\S+) 461 (?P<me>\S+) (?P<command>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NEEDMOREPARAMS)
    def myevent(bot, srv=None, me=None, command=None, data=None):
        # do something

ERR_NICK
--------

Match ``:(?P<srv>\S+) (?P<retcode>(432|433|436)) (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NICK)
    def myevent(bot):
        # do something

436 - ERR_NICKCOLLISION
-----------------------

Match ``^:(?P<srv>\S+) 436 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NICKCOLLISION)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

433 - ERR_NICKNAMEINUSE
-----------------------

Match ``^:(?P<srv>\S+) 433 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NICKNAMEINUSE)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

423 - ERR_NOADMININFO
---------------------

Match ``^:(?P<srv>\S+) 423 (?P<me>\S+) (?P<server>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOADMININFO)
    def myevent(bot, srv=None, me=None, server=None, data=None):
        # do something

444 - ERR_NOLOGIN
-----------------

Match ``^:(?P<srv>\S+) 444 (?P<me>\S+) (?P<user>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOLOGIN)
    def myevent(bot, srv=None, me=None, user=None, data=None):
        # do something

422 - ERR_NOMOTD
----------------

Match ``^:(?P<srv>\S+) 422 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOMOTD)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

431 - ERR_NONICKNAMEGIVEN
-------------------------

Match ``^:(?P<srv>\S+) 431 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NONICKNAMEGIVEN)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

491 - ERR_NOOPERHOST
--------------------

Match ``^:(?P<srv>\S+) 491 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOOPERHOST)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

409 - ERR_NOORIGIN
------------------

Match ``^:(?P<srv>\S+) 409 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOORIGIN)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

463 - ERR_NOPERMFORHOST
-----------------------

Match ``^:(?P<srv>\S+) 463 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOPERMFORHOST)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

481 - ERR_NOPRIVILEGES
----------------------

Match ``^:(?P<srv>\S+) 481 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOPRIVILEGES)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

411 - ERR_NORECIPIENT
---------------------

Match ``^:(?P<srv>\S+) 411 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NORECIPIENT)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

403 - ERR_NOSUCHCHANNEL
-----------------------

Match ``^:(?P<srv>\S+) 403 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOSUCHCHANNEL)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

401 - ERR_NOSUCHNICK
--------------------

Match ``^:(?P<srv>\S+) 401 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOSUCHNICK)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

402 - ERR_NOSUCHSERVER
----------------------

Match ``^:(?P<srv>\S+) 402 (?P<me>\S+) (?P<server>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOSUCHSERVER)
    def myevent(bot, srv=None, me=None, server=None, data=None):
        # do something

412 - ERR_NOTEXTTOSEND
----------------------

Match ``^:(?P<srv>\S+) 412 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOTEXTTOSEND)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

442 - ERR_NOTONCHANNEL
----------------------

Match ``^:(?P<srv>\S+) 442 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOTONCHANNEL)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

413 - ERR_NOTOPLEVEL
--------------------

Match ``^:(?P<srv>\S+) 413 (?P<me>\S+) (?P<mask>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOTOPLEVEL)
    def myevent(bot, srv=None, me=None, mask=None, data=None):
        # do something

451 - ERR_NOTREGISTERED
-----------------------

Match ``^:(?P<srv>\S+) 451 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOTREGISTERED)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

464 - ERR_PASSWDMISMATCH
------------------------

Match ``^:(?P<srv>\S+) 464 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_PASSWDMISMATCH)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

445 - ERR_SUMMONDISABLED
------------------------

Match ``^:(?P<srv>\S+) 445 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_SUMMONDISABLED)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

405 - ERR_TOOMANYCHANNELS
-------------------------

Match ``^:(?P<srv>\S+) 405 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_TOOMANYCHANNELS)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

407 - ERR_TOOMANYTARGETS
------------------------

Match ``^:(?P<srv>\S+) 407 (?P<me>\S+) (?P<target>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_TOOMANYTARGETS)
    def myevent(bot, srv=None, me=None, target=None, data=None):
        # do something

501 - ERR_UMODEUNKNOWNFLAG
--------------------------

Match ``^:(?P<srv>\S+) 501 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_UMODEUNKNOWNFLAG)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

421 - ERR_UNKNOWNCOMMAND
------------------------

Match ``^:(?P<srv>\S+) 421 (?P<me>\S+) (?P<command>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_UNKNOWNCOMMAND)
    def myevent(bot, srv=None, me=None, command=None, data=None):
        # do something

472 - ERR_UNKNOWNMODE
---------------------

Match ``^:(?P<srv>\S+) 472 (?P<me>\S+) (?P<char>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_UNKNOWNMODE)
    def myevent(bot, srv=None, me=None, char=None, data=None):
        # do something

441 - ERR_USERNOTINCHANNEL
--------------------------

Match ``^:(?P<srv>\S+) 441 (?P<me>\S+) (?P<nick>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_USERNOTINCHANNEL)
    def myevent(bot, srv=None, me=None, nick=None, channel=None, data=None):
        # do something

443 - ERR_USERONCHANNEL
-----------------------

Match ``^:(?P<srv>\S+) 443 (?P<me>\S+) (?P<user>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_USERONCHANNEL)
    def myevent(bot, srv=None, me=None, user=None, channel=None, data=None):
        # do something

446 - ERR_USERSDISABLED
-----------------------

Match ``^:(?P<srv>\S+) 446 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_USERSDISABLED)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

502 - ERR_USERSDONTMATCH
------------------------

Match ``^:(?P<srv>\S+) 502 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_USERSDONTMATCH)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

406 - ERR_WASNOSUCHNICK
-----------------------

Match ``^:(?P<srv>\S+) 406 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_WASNOSUCHNICK)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

414 - ERR_WILDTOPLEVEL
----------------------

Match ``^:(?P<srv>\S+) 414 (?P<me>\S+) (?P<mask>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_WILDTOPLEVEL)
    def myevent(bot, srv=None, me=None, mask=None, data=None):
        # do something

465 - ERR_YOUREBANNEDCREEP
--------------------------

Match ``^:(?P<srv>\S+) 465 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_YOUREBANNEDCREEP)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

Misc
====

CTCP
----

Match ``:(?P<mask>\S+!\S+@\S+) (?P<event>(PRIVMSG|NOTICE)) {nick} :(?P<ctcp>\S+.*)$``

Example:

.. code-block:: python

    @irc3.event(rfc.CTCP)
    def myevent(bot):
        # do something

JOIN
----

Match ``:(?P<mask>\S+) JOIN (?P<channel>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.JOIN)
    def myevent(bot):
        # do something

JOIN_PART_QUIT
--------------

Match ``:(?P<mask>\S+) (?P<event>JOIN|PART|QUIT)\s*(?P<channel>\S*)(\s+:(?P<data>.*)|$)``

Example:

.. code-block:: python

    @irc3.event(rfc.JOIN_PART_QUIT)
    def myevent(bot):
        # do something

MY_PRIVMSG
----------

Match ``:(?P<mask>\S+!\S+@\S+) (?P<event>(PRIVMSG|NOTICE)) (?P<target>(#\S+|{nick})) :{nick}[:,\s]\s*(?P<data>\S+.*)$``

Example:

.. code-block:: python

    @irc3.event(rfc.MY_PRIVMSG)
    def myevent(bot):
        # do something

NEW_NICK
--------

Match ``:(?P<nick>\S+) NICK (?P<new_nick>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.NEW_NICK)
    def myevent(bot):
        # do something

PART
----

Match ``:(?P<mask>\S+) PART (?P<channel>\S+)(\s+:(?P<data>.*)|$)``

Example:

.. code-block:: python

    @irc3.event(rfc.PART)
    def myevent(bot):
        # do something

PING
----

Match ``PING :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.PING)
    def myevent(bot):
        # do something

PRIVMSG
-------

Match ``:(?P<mask>\S+!\S+@\S+) (?P<event>(PRIVMSG|NOTICE)) (?P<target>\S+) :\s*(?P<data>\S+.*)$``

Example:

.. code-block:: python

    @irc3.event(rfc.PRIVMSG)
    def myevent(bot):
        # do something

QUIT
----

Match ``:(?P<mask>\S+) QUIT(\s+:(?P<data>.*)|$)``

Example:

.. code-block:: python

    @irc3.event(rfc.QUIT)
    def myevent(bot):
        # do something

