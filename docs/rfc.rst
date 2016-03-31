========================
:mod:`irc3.rfc` RFC1459
========================

Replies (REPL)
==============

259 - RPL_ADMINEMAIL
--------------------

Format ``:{srv} 259 {nick} :{admin_info}``

Match ``^:(?P<srv>\S+) 259 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ADMINEMAIL)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

257 - RPL_ADMINLOC1
-------------------

Format ``:{srv} 257 {nick} :{admin_info}``

Match ``^:(?P<srv>\S+) 257 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ADMINLOC1)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

258 - RPL_ADMINLOC2
-------------------

Format ``:{srv} 258 {nick} :{admin_info}``

Match ``^:(?P<srv>\S+) 258 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ADMINLOC2)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

256 - RPL_ADMINME
-----------------

Format ``:{srv} 256 {nick} {server} :Administrative info``

Match ``^:(?P<srv>\S+) 256 (?P<me>\S+) (?P<server>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ADMINME)
    def myevent(bot, srv=None, me=None, server=None, data=None):
        # do something

301 - RPL_AWAY
--------------

Format ``:{srv} 301 {nick} {nick} :{away_message}``

Match ``^:(?P<srv>\S+) 301 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_AWAY)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

367 - RPL_BANLIST
-----------------

Format ``:{srv} 367 {nick} {channel} {banid}``

Match ``^:(?P<srv>\S+) 367 (?P<me>\S+) (?P<channel>\S+) (?P<banid>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_BANLIST)
    def myevent(bot, srv=None, me=None, channel=None, banid=None):
        # do something

324 - RPL_CHANNELMODEIS
-----------------------

Format ``:{srv} 324 {nick} {channel} {mode} {mode_params}``

Match ``^:(?P<srv>\S+) 324 (?P<me>\S+) (?P<channel>\S+) (?P<mode>\S+) (?P<mode_params>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_CHANNELMODEIS)
    def myevent(bot, srv=None, me=None, channel=None, mode=None, mode_params=None):
        # do something

368 - RPL_ENDOFBANLIST
----------------------

Format ``:{srv} 368 {nick} {channel} :End of channel ban list``

Match ``^:(?P<srv>\S+) 368 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFBANLIST)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

374 - RPL_ENDOFINFO
-------------------

Format ``:{srv} 374 {nick} :End of /INFO list``

Match ``^:(?P<srv>\S+) 374 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFINFO)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

365 - RPL_ENDOFLINKS
--------------------

Format ``:{srv} 365 {nick} {mask} :End of /LINKS list``

Match ``^:(?P<srv>\S+) 365 (?P<me>\S+) (?P<mask>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFLINKS)
    def myevent(bot, srv=None, me=None, mask=None, data=None):
        # do something

376 - RPL_ENDOFMOTD
-------------------

Format ``:{srv} 376 {nick} :End of /MOTD command``

Match ``^:(?P<srv>\S+) 376 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFMOTD)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

366 - RPL_ENDOFNAMES
--------------------

Format ``:{srv} 366 {nick} {channel} :End of /NAMES list``

Match ``^:(?P<srv>\S+) 366 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFNAMES)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

219 - RPL_ENDOFSTATS
--------------------

Format ``:{srv} 219 {nick} {stats_letter} :End of /STATS report``

Match ``^:(?P<srv>\S+) 219 (?P<me>\S+) (?P<stats_letter>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFSTATS)
    def myevent(bot, srv=None, me=None, stats_letter=None, data=None):
        # do something

394 - RPL_ENDOFUSERS
--------------------

Format ``:{srv} 394 {nick} :End of users``

Match ``^:(?P<srv>\S+) 394 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFUSERS)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

315 - RPL_ENDOFWHO
------------------

Format ``:{srv} 315 {nick} {nick} :End of /WHO list``

Match ``^:(?P<srv>\S+) 315 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFWHO)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

318 - RPL_ENDOFWHOIS
--------------------

Format ``:{srv} 318 {nick} {nick} :End of /WHOIS list``

Match ``^:(?P<srv>\S+) 318 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFWHOIS)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

369 - RPL_ENDOFWHOWAS
---------------------

Format ``:{srv} 369 {nick} {nick} :End of WHOWAS``

Match ``^:(?P<srv>\S+) 369 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ENDOFWHOWAS)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

371 - RPL_INFO
--------------

Format ``:{srv} 371 {nick} :{string}``

Match ``^:(?P<srv>\S+) 371 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_INFO)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

341 - RPL_INVITING
------------------

Format ``:{srv} 341 {nick} {channel} {nick}``

Match ``^:(?P<srv>\S+) 341 (?P<me>\S+) (?P<channel>\S+) (?P<nick>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_INVITING)
    def myevent(bot, srv=None, me=None, channel=None, nick=None):
        # do something

303 - RPL_ISON
--------------

Format ``:{srv} 303 {nick} :{nicknames}``

Match ``^:(?P<srv>\S+) 303 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_ISON)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

364 - RPL_LINKS
---------------

Format ``:{srv} 364 {nick} {mask} {server} :{hopcount} {server_info}``

Match ``^:(?P<srv>\S+) 364 (?P<me>\S+) (?P<mask>\S+) (?P<server>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LINKS)
    def myevent(bot, srv=None, me=None, mask=None, server=None, data=None):
        # do something

322 - RPL_LIST
--------------

Format ``:{srv} 322 {nick} {channel} {visible} :{topic}``

Match ``^:(?P<srv>\S+) 322 (?P<me>\S+) (?P<channel>\S+) (?P<visible>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LIST)
    def myevent(bot, srv=None, me=None, channel=None, visible=None, data=None):
        # do something

323 - RPL_LISTEND
-----------------

Format ``:{srv} 323 {nick} :End of /LIST``

Match ``^:(?P<srv>\S+) 323 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LISTEND)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

321 - RPL_LISTSTART
-------------------

Format ``:{srv} 321 {nick} Channel :Users  Name``

Match ``^:(?P<srv>\S+) 321 (?P<me>\S+) Channel :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LISTSTART)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

254 - RPL_LUSERCHANNELS
-----------------------

Format ``:{srv} 254 {nick} {x} :channels formed``

Match ``^:(?P<srv>\S+) 254 (?P<me>\S+) (?P<x>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LUSERCHANNELS)
    def myevent(bot, srv=None, me=None, x=None, data=None):
        # do something

251 - RPL_LUSERCLIENT
---------------------

Format ``:{srv} 251 {nick} :There are {x} users and {y} invisible on {z} servers``

Match ``^:(?P<srv>\S+) 251 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LUSERCLIENT)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

255 - RPL_LUSERME
-----------------

Format ``:{srv} 255 {nick} :I have {x} clients and {y}``

Match ``^:(?P<srv>\S+) 255 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LUSERME)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

252 - RPL_LUSEROP
-----------------

Format ``:{srv} 252 {nick} {x} :operator(s) online``

Match ``^:(?P<srv>\S+) 252 (?P<me>\S+) (?P<x>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LUSEROP)
    def myevent(bot, srv=None, me=None, x=None, data=None):
        # do something

253 - RPL_LUSERUNKNOWN
----------------------

Format ``:{srv} 253 {nick} {x} :unknown connection(s)``

Match ``^:(?P<srv>\S+) 253 (?P<me>\S+) (?P<x>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_LUSERUNKNOWN)
    def myevent(bot, srv=None, me=None, x=None, data=None):
        # do something

372 - RPL_MOTD
--------------

Format ``:{srv} 372 {nick} :- {text}``

Match ``^:(?P<srv>\S+) 372 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_MOTD)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

375 - RPL_MOTDSTART
-------------------

Format ``:{srv} 375 {nick} :- {server} Message of the day -``

Match ``^:(?P<srv>\S+) 375 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_MOTDSTART)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

353 - RPL_NAMREPLY
------------------

Format ``:{srv} 353 {nick} {m} {channel} :{nicknames}``

Match ``^:(?P<srv>\S+) 353 (?P<me>\S+) (?P<m>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_NAMREPLY)
    def myevent(bot, srv=None, me=None, m=None, channel=None, data=None):
        # do something

331 - RPL_NOTOPIC
-----------------

Format ``:{srv} 331 {nick} {channel} :No topic is set``

Match ``^:(?P<srv>\S+) 331 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_NOTOPIC)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

395 - RPL_NOUSERS
-----------------

Format ``:{srv} 395 {nick} :Nobody logged in``

Match ``^:(?P<srv>\S+) 395 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_NOUSERS)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

306 - RPL_NOWAWAY
-----------------

Format ``:{srv} 306 {nick} :You have been marked as being away``

Match ``^:(?P<srv>\S+) 306 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_NOWAWAY)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

382 - RPL_REHASHING
-------------------

Format ``:{srv} 382 {nick} {config_file} :Rehashing``

Match ``^:(?P<srv>\S+) 382 (?P<me>\S+) (?P<config_file>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_REHASHING)
    def myevent(bot, srv=None, me=None, config_file=None, data=None):
        # do something

213 - RPL_STATSCLINE
--------------------

Format ``:{srv} 213 {nick} C {host} * {nick} {port} {class}``

Match ``^:(?P<srv>\S+) 213 (?P<me>\S+) C (?P<host>\S+) . (?P<nick>\S+) (?P<port>\S+) (?P<class>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSCLINE)
    def myevent(bot, srv=None, me=None, host=None, nick=None, port=None, class=None):
        # do something

212 - RPL_STATSCOMMANDS
-----------------------

Format ``:{srv} 212 {nick} {cmd} {count}``

Match ``^:(?P<srv>\S+) 212 (?P<me>\S+) (?P<cmd>\S+) (?P<count>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSCOMMANDS)
    def myevent(bot, srv=None, me=None, cmd=None, count=None):
        # do something

244 - RPL_STATSHLINE
--------------------

Format ``:{srv} 244 {nick} H {hostmask} * {servername}``

Match ``^:(?P<srv>\S+) 244 (?P<me>\S+) H (?P<hostmask>\S+) . (?P<servername>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSHLINE)
    def myevent(bot, srv=None, me=None, hostmask=None, servername=None):
        # do something

215 - RPL_STATSILINE
--------------------

Format ``:{srv} 215 {nick} I {host} * {host1} {port} {class}``

Match ``^:(?P<srv>\S+) 215 (?P<me>\S+) I (?P<host>\S+) . (?P<host1>\S+) (?P<port>\S+) (?P<class>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSILINE)
    def myevent(bot, srv=None, me=None, host=None, host1=None, port=None, class=None):
        # do something

216 - RPL_STATSKLINE
--------------------

Format ``:{srv} 216 {nick} K {host} * {username} {port} {class}``

Match ``^:(?P<srv>\S+) 216 (?P<me>\S+) K (?P<host>\S+) . (?P<username>\S+) (?P<port>\S+) (?P<class>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSKLINE)
    def myevent(bot, srv=None, me=None, host=None, username=None, port=None, class=None):
        # do something

211 - RPL_STATSLINKINFO
-----------------------

Format ``:{srv} 211 {nick} :{linkname} {sendq} {sent_messages} {received_bytes} {time_open}``

Match ``^:(?P<srv>\S+) 211 (?P<me>\S+) (?P<linkname>\S+) (?P<sendq>\S+) (?P<sent_messages>\S+) (?P<received_bytes>\S+) (?P<time_open>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSLINKINFO)
    def myevent(bot, srv=None, me=None, linkname=None, sendq=None, sent_messages=None, received_bytes=None, time_open=None):
        # do something

241 - RPL_STATSLLINE
--------------------

Format ``:{srv} 241 {nick} L {hostmask} * {servername} {maxdepth}``

Match ``^:(?P<srv>\S+) 241 (?P<me>\S+) L (?P<hostmask>\S+) . (?P<servername>\S+) (?P<maxdepth>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSLLINE)
    def myevent(bot, srv=None, me=None, hostmask=None, servername=None, maxdepth=None):
        # do something

214 - RPL_STATSNLINE
--------------------

Format ``:{srv} 214 {nick} N {host} * {nick} {port} {class}``

Match ``^:(?P<srv>\S+) 214 (?P<me>\S+) N (?P<host>\S+) . (?P<nick>\S+) (?P<port>\S+) (?P<class>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSNLINE)
    def myevent(bot, srv=None, me=None, host=None, nick=None, port=None, class=None):
        # do something

243 - RPL_STATSOLINE
--------------------

Format ``:{srv} 243 {nick} O {hostmask} * {nick}``

Match ``^:(?P<srv>\S+) 243 (?P<me>\S+) O (?P<hostmask>\S+) . (?P<nick>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSOLINE)
    def myevent(bot, srv=None, me=None, hostmask=None, nick=None):
        # do something

242 - RPL_STATSUPTIME
---------------------

Format ``:{srv} 242 {nick} :Server Up{days}days {hours}``

Match ``^:(?P<srv>\S+) 242 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSUPTIME)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

218 - RPL_STATSYLINE
--------------------

Format ``:{srv} 218 {nick} frequency> {max_sendq}``

Match ``^:(?P<srv>\S+) 218 (?P<me>\S+) frequency> (?P<max_sendq>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_STATSYLINE)
    def myevent(bot, srv=None, me=None, max_sendq=None):
        # do something

342 - RPL_SUMMONING
-------------------

Format ``:{srv} 342 {nick} {nick} :Summoning user to IRC``

Match ``^:(?P<srv>\S+) 342 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_SUMMONING)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

391 - RPL_TIME
--------------

Format ``:{srv} 391 {nick} {server} :{string_showing_server's_local_time}``

Match ``^:(?P<srv>\S+) 391 (?P<me>\S+) (?P<server>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TIME)
    def myevent(bot, srv=None, me=None, server=None, data=None):
        # do something

332 - RPL_TOPIC
---------------

Format ``:{srv} 332 {nick} {channel} :{topic}``

Match ``^:(?P<srv>\S+) 332 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TOPIC)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

201 - RPL_TRACECONNECTING
-------------------------

Format ``:{srv} 201 {nick} Try. {class} {server}``

Match ``^:(?P<srv>\S+) 201 (?P<me>\S+) Try. (?P<class>\S+) (?P<server>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACECONNECTING)
    def myevent(bot, srv=None, me=None, class=None, server=None):
        # do something

202 - RPL_TRACEHANDSHAKE
------------------------

Format ``:{srv} 202 {nick} H.S. {class} {server}``

Match ``^:(?P<srv>\S+) 202 (?P<me>\S+) H.S. (?P<class>\S+) (?P<server>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACEHANDSHAKE)
    def myevent(bot, srv=None, me=None, class=None, server=None):
        # do something

200 - RPL_TRACELINK
-------------------

Format ``:{srv} 200 {nick} {next_server}``

Match ``^:(?P<srv>\S+) 200 (?P<me>\S+) (?P<next_server>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACELINK)
    def myevent(bot, srv=None, me=None, next_server=None):
        # do something

261 - RPL_TRACELOG
------------------

Format ``:{srv} 261 {nick} File {logfile} {debug_level}``

Match ``^:(?P<srv>\S+) 261 (?P<me>\S+) File (?P<logfile>\S+) (?P<debug_level>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACELOG)
    def myevent(bot, srv=None, me=None, logfile=None, debug_level=None):
        # do something

208 - RPL_TRACENEWTYPE
----------------------

Format ``:{srv} 208 {nick} {newtype} 0 {client}``

Match ``^:(?P<srv>\S+) 208 (?P<me>\S+) (?P<newtype>\S+) 0 (?P<client>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACENEWTYPE)
    def myevent(bot, srv=None, me=None, newtype=None, client=None):
        # do something

204 - RPL_TRACEOPERATOR
-----------------------

Format ``:{srv} 204 {nick} Oper {class} {nick}``

Match ``^:(?P<srv>\S+) 204 (?P<me>\S+) Oper (?P<class>\S+) (?P<nick>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACEOPERATOR)
    def myevent(bot, srv=None, me=None, class=None, nick=None):
        # do something

206 - RPL_TRACESERVER
---------------------

Format ``:{srv} 206 {nick} {mask}``

Match ``^:(?P<srv>\S+) 206 (?P<me>\S+) (?P<mask>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACESERVER)
    def myevent(bot, srv=None, me=None, mask=None):
        # do something

203 - RPL_TRACEUNKNOWN
----------------------

Format ``:{srv} 203 {nick} ???? {class} [{clientip}]``

Match ``^:(?P<srv>\S+) 203 (?P<me>\S+) \S+ (?P<class>\S+) [(?P<clientip>\S+)]``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACEUNKNOWN)
    def myevent(bot, srv=None, me=None, class=None, clientip=None):
        # do something

205 - RPL_TRACEUSER
-------------------

Format ``:{srv} 205 {nick} User {class} {nick}``

Match ``^:(?P<srv>\S+) 205 (?P<me>\S+) User (?P<class>\S+) (?P<nick>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_TRACEUSER)
    def myevent(bot, srv=None, me=None, class=None, nick=None):
        # do something

221 - RPL_UMODEIS
-----------------

Format ``:{srv} 221 {nick} {user_mode_string}``

Match ``^:(?P<srv>\S+) 221 (?P<me>\S+) (?P<user_mode_string>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_UMODEIS)
    def myevent(bot, srv=None, me=None, user_mode_string=None):
        # do something

305 - RPL_UNAWAY
----------------

Format ``:{srv} 305 {nick} :You are no longer marked as being away``

Match ``^:(?P<srv>\S+) 305 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_UNAWAY)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

302 - RPL_USERHOST
------------------

Format ``:{srv} 302 {nick} :[{reply}{{space}{reply}}]``

Match ``^:(?P<srv>\S+) 302 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_USERHOST)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

393 - RPL_USERS
---------------

Format ``:{srv} 393 {nick} {x} {y} {z}``

Match ``^:(?P<srv>\S+) 393 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_USERS)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

392 - RPL_USERSSTART
--------------------

Format ``:{srv} 392 {nick} :UserID   Terminal  Host``

Match ``^:(?P<srv>\S+) 392 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_USERSSTART)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

351 - RPL_VERSION
-----------------

Format ``:{srv} 351 {nick} {version}.{debuglevel} {server} :{comments}``

Match ``^:(?P<srv>\S+) 351 (?P<me>\S+) (?P<version>\S+).(?P<debuglevel>\S+) (?P<server>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_VERSION)
    def myevent(bot, srv=None, me=None, version=None, debuglevel=None, server=None, data=None):
        # do something

319 - RPL_WHOISCHANNELS
-----------------------

Format ``:{srv} 319 {nick} :{channels}``

Match ``^:(?P<srv>\S+) 319 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_WHOISCHANNELS)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

317 - RPL_WHOISIDLE
-------------------

Format ``:{srv} 317 {nick} {nick} {x} :seconds idle``

Match ``^:(?P<srv>\S+) 317 (?P<me>\S+) (?P<nick>\S+) (?P<x>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_WHOISIDLE)
    def myevent(bot, srv=None, me=None, nick=None, x=None, data=None):
        # do something

313 - RPL_WHOISOPERATOR
-----------------------

Format ``:{srv} 313 {nick} {nick} :is an IRC operator``

Match ``^:(?P<srv>\S+) 313 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_WHOISOPERATOR)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

312 - RPL_WHOISSERVER
---------------------

Format ``:{srv} 312 {nick} {nick} {server} :{server_info}``

Match ``^:(?P<srv>\S+) 312 (?P<me>\S+) (?P<nick>\S+) (?P<server>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_WHOISSERVER)
    def myevent(bot, srv=None, me=None, nick=None, server=None, data=None):
        # do something

311 - RPL_WHOISUSER
-------------------

Format ``:{srv} 311 {nick} {nick} {username} {host} {m} :{realname}``

Match ``^:(?P<srv>\S+) 311 (?P<me>\S+) (?P<nick>\S+) (?P<username>\S+) (?P<host>\S+) (?P<m>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_WHOISUSER)
    def myevent(bot, srv=None, me=None, nick=None, username=None, host=None, m=None, data=None):
        # do something

352 - RPL_WHOREPLY
------------------

Format ``:{srv} 352 {nick} :{channel} {username} {host} {server} {nick} {modes} :{hopcount} {realname}``

Match ``^:(?P<srv>\S+) 352 (?P<me>\S+) (?P<channel>\S+) (?P<username>\S+) (?P<host>\S+) (?P<server>\S+) (?P<nick>\S+) (?P<modes>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_WHOREPLY)
    def myevent(bot, srv=None, me=None, channel=None, username=None, host=None, server=None, nick=None, modes=None, data=None):
        # do something

314 - RPL_WHOWASUSER
--------------------

Format ``:{srv} 314 {nick} {nick} {username} {host} * :{realname}``

Match ``^:(?P<srv>\S+) 314 (?P<me>\S+) (?P<nick>\S+) (?P<username>\S+) (?P<host>\S+) . :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.RPL_WHOWASUSER)
    def myevent(bot, srv=None, me=None, nick=None, username=None, host=None, data=None):
        # do something

381 - RPL_YOUREOPER
-------------------

Format ``:{srv} 381 {nick} :You are now an IRC operator``

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

Format ``:{srv} 462 {nick} :You may not reregister``

Match ``^:(?P<srv>\S+) 462 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_ALREADYREGISTRED)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

475 - ERR_BADCHANNELKEY
-----------------------

Format ``:{srv} 475 {nick} {channel} :Cannot join channel (+k)``

Match ``^:(?P<srv>\S+) 475 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_BADCHANNELKEY)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

474 - ERR_BANNEDFROMCHAN
------------------------

Format ``:{srv} 474 {nick} {channel} :Cannot join channel (+b)``

Match ``^:(?P<srv>\S+) 474 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_BANNEDFROMCHAN)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

404 - ERR_CANNOTSENDTOCHAN
--------------------------

Format ``:{srv} 404 {nick} {channel} :Cannot send to channel``

Match ``^:(?P<srv>\S+) 404 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_CANNOTSENDTOCHAN)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

483 - ERR_CANTKILLSERVER
------------------------

Format ``:{srv} 483 {nick} :You cant kill a server!``

Match ``^:(?P<srv>\S+) 483 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_CANTKILLSERVER)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

471 - ERR_CHANNELISFULL
-----------------------

Format ``:{srv} 471 {nick} {channel} :Cannot join channel (+l)``

Match ``^:(?P<srv>\S+) 471 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_CHANNELISFULL)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

482 - ERR_CHANOPRIVSNEEDED
--------------------------

Format ``:{srv} 482 {nick} {channel} :You're not channel operator``

Match ``^:(?P<srv>\S+) 482 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_CHANOPRIVSNEEDED)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

432 - ERR_ERRONEUSNICKNAME
--------------------------

Format ``:{srv} 432 {nick} {nick} :Erroneus nickname``

Match ``^:(?P<srv>\S+) 432 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_ERRONEUSNICKNAME)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

473 - ERR_INVITEONLYCHAN
------------------------

Format ``:{srv} 473 {nick} {channel} :Cannot join channel (+i)``

Match ``^:(?P<srv>\S+) 473 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_INVITEONLYCHAN)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

467 - ERR_KEYSET
----------------

Format ``:{srv} 467 {nick} {channel} :Channel key already set``

Match ``^:(?P<srv>\S+) 467 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_KEYSET)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

461 - ERR_NEEDMOREPARAMS
------------------------

Format ``:{srv} 461 {nick} {cmd} :Not enough parameters``

Match ``^:(?P<srv>\S+) 461 (?P<me>\S+) (?P<cmd>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NEEDMOREPARAMS)
    def myevent(bot, srv=None, me=None, cmd=None, data=None):
        # do something

ERR_NICK
--------

Match ``^(@(?P<tags>\S+) )?:(?P<srv>\S+) (?P<retcode>(432|433|436)) (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NICK)
    def myevent(bot):
        # do something

436 - ERR_NICKCOLLISION
-----------------------

Format ``:{srv} 436 {nick} {nick} :Nickname collision KILL``

Match ``^:(?P<srv>\S+) 436 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NICKCOLLISION)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

433 - ERR_NICKNAMEINUSE
-----------------------

Format ``:{srv} 433 {nick} {nick} :Nickname is already in use``

Match ``^:(?P<srv>\S+) 433 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NICKNAMEINUSE)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

423 - ERR_NOADMININFO
---------------------

Format ``:{srv} 423 {nick} {server} :No administrative info available``

Match ``^:(?P<srv>\S+) 423 (?P<me>\S+) (?P<server>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOADMININFO)
    def myevent(bot, srv=None, me=None, server=None, data=None):
        # do something

444 - ERR_NOLOGIN
-----------------

Format ``:{srv} 444 {nick} {nick} :User not logged in``

Match ``^:(?P<srv>\S+) 444 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOLOGIN)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

422 - ERR_NOMOTD
----------------

Format ``:{srv} 422 {nick} :MOTD File is missing``

Match ``^:(?P<srv>\S+) 422 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOMOTD)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

431 - ERR_NONICKNAMEGIVEN
-------------------------

Format ``:{srv} 431 {nick} :No nickname given``

Match ``^:(?P<srv>\S+) 431 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NONICKNAMEGIVEN)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

491 - ERR_NOOPERHOST
--------------------

Format ``:{srv} 491 {nick} :No O-lines for your host``

Match ``^:(?P<srv>\S+) 491 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOOPERHOST)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

409 - ERR_NOORIGIN
------------------

Format ``:{srv} 409 {nick} :No origin specified``

Match ``^:(?P<srv>\S+) 409 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOORIGIN)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

463 - ERR_NOPERMFORHOST
-----------------------

Format ``:{srv} 463 {nick} :Your host isn't among the privileged``

Match ``^:(?P<srv>\S+) 463 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOPERMFORHOST)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

481 - ERR_NOPRIVILEGES
----------------------

Format ``:{srv} 481 {nick} :Permission Denied- You're not an IRC operator``

Match ``^:(?P<srv>\S+) 481 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOPRIVILEGES)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

411 - ERR_NORECIPIENT
---------------------

Format ``:{srv} 411 {nick} :No recipient given ({cmd})``

Match ``^:(?P<srv>\S+) 411 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NORECIPIENT)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

403 - ERR_NOSUCHCHANNEL
-----------------------

Format ``:{srv} 403 {nick} {channel} :No such channel``

Match ``^:(?P<srv>\S+) 403 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOSUCHCHANNEL)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

401 - ERR_NOSUCHNICK
--------------------

Format ``:{srv} 401 {nick} {nick} :No such nick/channel``

Match ``^:(?P<srv>\S+) 401 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOSUCHNICK)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

402 - ERR_NOSUCHSERVER
----------------------

Format ``:{srv} 402 {nick} {server} :No such server``

Match ``^:(?P<srv>\S+) 402 (?P<me>\S+) (?P<server>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOSUCHSERVER)
    def myevent(bot, srv=None, me=None, server=None, data=None):
        # do something

412 - ERR_NOTEXTTOSEND
----------------------

Format ``:{srv} 412 {nick} :No text to send``

Match ``^:(?P<srv>\S+) 412 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOTEXTTOSEND)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

442 - ERR_NOTONCHANNEL
----------------------

Format ``:{srv} 442 {nick} {channel} :You're not on that channel``

Match ``^:(?P<srv>\S+) 442 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOTONCHANNEL)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

413 - ERR_NOTOPLEVEL
--------------------

Format ``:{srv} 413 {nick} {mask} :No toplevel domain specified``

Match ``^:(?P<srv>\S+) 413 (?P<me>\S+) (?P<mask>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOTOPLEVEL)
    def myevent(bot, srv=None, me=None, mask=None, data=None):
        # do something

451 - ERR_NOTREGISTERED
-----------------------

Format ``:{srv} 451 {nick} :You have not registered``

Match ``^:(?P<srv>\S+) 451 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_NOTREGISTERED)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

464 - ERR_PASSWDMISMATCH
------------------------

Format ``:{srv} 464 {nick} :Password incorrect``

Match ``^:(?P<srv>\S+) 464 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_PASSWDMISMATCH)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

445 - ERR_SUMMONDISABLED
------------------------

Format ``:{srv} 445 {nick} :SUMMON has been disabled``

Match ``^:(?P<srv>\S+) 445 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_SUMMONDISABLED)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

405 - ERR_TOOMANYCHANNELS
-------------------------

Format ``:{srv} 405 {nick} {channel} :You have joined too many channels``

Match ``^:(?P<srv>\S+) 405 (?P<me>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_TOOMANYCHANNELS)
    def myevent(bot, srv=None, me=None, channel=None, data=None):
        # do something

407 - ERR_TOOMANYTARGETS
------------------------

Format ``:{srv} 407 {nick} {target} :Duplicate recipients. No message delivered``

Match ``^:(?P<srv>\S+) 407 (?P<me>\S+) (?P<target>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_TOOMANYTARGETS)
    def myevent(bot, srv=None, me=None, target=None, data=None):
        # do something

501 - ERR_UMODEUNKNOWNFLAG
--------------------------

Format ``:{srv} 501 {nick} :Unknown MODE flag``

Match ``^:(?P<srv>\S+) 501 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_UMODEUNKNOWNFLAG)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

421 - ERR_UNKNOWNCOMMAND
------------------------

Format ``:{srv} 421 {nick} {cmd} :Unknown command``

Match ``^:(?P<srv>\S+) 421 (?P<me>\S+) (?P<cmd>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_UNKNOWNCOMMAND)
    def myevent(bot, srv=None, me=None, cmd=None, data=None):
        # do something

472 - ERR_UNKNOWNMODE
---------------------

Format ``:{srv} 472 {nick} {char} :is unknown mode char to me``

Match ``^:(?P<srv>\S+) 472 (?P<me>\S+) (?P<char>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_UNKNOWNMODE)
    def myevent(bot, srv=None, me=None, char=None, data=None):
        # do something

441 - ERR_USERNOTINCHANNEL
--------------------------

Format ``:{srv} 441 {nick} {nick} {channel} :They aren't on that channel``

Match ``^:(?P<srv>\S+) 441 (?P<me>\S+) (?P<nick>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_USERNOTINCHANNEL)
    def myevent(bot, srv=None, me=None, nick=None, channel=None, data=None):
        # do something

443 - ERR_USERONCHANNEL
-----------------------

Format ``:{srv} 443 {nick} {nick} {channel} :is already on channel``

Match ``^:(?P<srv>\S+) 443 (?P<me>\S+) (?P<nick>\S+) (?P<channel>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_USERONCHANNEL)
    def myevent(bot, srv=None, me=None, nick=None, channel=None, data=None):
        # do something

446 - ERR_USERSDISABLED
-----------------------

Format ``:{srv} 446 {nick} :USERS has been disabled``

Match ``^:(?P<srv>\S+) 446 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_USERSDISABLED)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

502 - ERR_USERSDONTMATCH
------------------------

Format ``:{srv} 502 {nick} :Cant change mode for other users``

Match ``^:(?P<srv>\S+) 502 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_USERSDONTMATCH)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

406 - ERR_WASNOSUCHNICK
-----------------------

Format ``:{srv} 406 {nick} {nick} :There was no such nickname``

Match ``^:(?P<srv>\S+) 406 (?P<me>\S+) (?P<nick>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_WASNOSUCHNICK)
    def myevent(bot, srv=None, me=None, nick=None, data=None):
        # do something

414 - ERR_WILDTOPLEVEL
----------------------

Format ``:{srv} 414 {nick} {mask} :Wildcard in toplevel domain``

Match ``^:(?P<srv>\S+) 414 (?P<me>\S+) (?P<mask>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_WILDTOPLEVEL)
    def myevent(bot, srv=None, me=None, mask=None, data=None):
        # do something

465 - ERR_YOUREBANNEDCREEP
--------------------------

Format ``:{srv} 465 {nick} :You are banned from this server``

Match ``^:(?P<srv>\S+) 465 (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.ERR_YOUREBANNEDCREEP)
    def myevent(bot, srv=None, me=None, data=None):
        # do something

Misc
====

CONNECTED
---------

Match ``^:(?P<srv>\S+) (376|422) (?P<me>\S+) :(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.CONNECTED)
    def myevent(bot):
        # do something

CTCP
----

Match ``^(@(?P<tags>\S+) )?:(?P<mask>\S+!\S+@\S+) (?P<event>(PRIVMSG|NOTICE)) {nick} :(?P<ctcp>\S+.*)$``

Example:

.. code-block:: python

    @irc3.event(rfc.CTCP)
    def myevent(bot):
        # do something

INVITE
------

Match ``^(@(?P<tags>\S+) )?:(?P<mask>\S+!\S+@\S+) INVITE {nick} :?(?P<channel>\S+)$``

Example:

.. code-block:: python

    @irc3.event(rfc.INVITE)
    def myevent(bot):
        # do something

JOIN
----

Match ``^(@(?P<tags>\S+) )?:(?P<mask>\S+) JOIN :?(?P<channel>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.JOIN)
    def myevent(bot):
        # do something

JOIN_PART_QUIT
--------------

Match ``^(@(?P<tags>\S+) )?:(?P<mask>\S+) (?P<event>JOIN|PART|QUIT)\s*:*(?P<channel>\S*)(\s+:(?P<data>.*)|$)``

Example:

.. code-block:: python

    @irc3.event(rfc.JOIN_PART_QUIT)
    def myevent(bot):
        # do something

KICK
----

Match ``^(@(?P<tags>\S+) )?:(?P<mask>\S+) (?P<event>KICK)\s+(?P<channel>\S+)\s*(?P<target>\S+)(\s+:(?P<data>.*)|$)``

Example:

.. code-block:: python

    @irc3.event(rfc.KICK)
    def myevent(bot):
        # do something

MODE
----

Match ``^(@(?P<tags>\S+) )?:(?P<mask>\S+) (?P<event>MODE)\s+(?P<target>\S+)\s+(?P<modes>\S+)(\s+(?P<data>.*)|$)``

Example:

.. code-block:: python

    @irc3.event(rfc.MODE)
    def myevent(bot):
        # do something

MY_PRIVMSG
----------

Match ``^(@(?P<tags>\S+) )?:(?P<mask>\S+!\S+@\S+) (?P<event>(PRIVMSG|NOTICE)) (?P<target>(#\S+|{nick})) :{nick}[:,\s]\s*(?P<data>\S+.*)$``

Example:

.. code-block:: python

    @irc3.event(rfc.MY_PRIVMSG)
    def myevent(bot):
        # do something

NEW_NICK
--------

Match ``^(@(?P<tags>\S+) )?:(?P<nick>\S+) NICK :?(?P<new_nick>\S+)``

Example:

.. code-block:: python

    @irc3.event(rfc.NEW_NICK)
    def myevent(bot):
        # do something

PART
----

Match ``^(@(?P<tags>\S+) )?:(?P<mask>\S+) PART (?P<channel>\S+)(\s+:(?P<data>.*)|$)``

Example:

.. code-block:: python

    @irc3.event(rfc.PART)
    def myevent(bot):
        # do something

PING
----

Match ``^PING :?(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.PING)
    def myevent(bot):
        # do something

PONG
----

Match ``^(@(?P<tags>\S+) )?:(?P<server>\S+) PONG (?P=server) :?(?P<data>.*)``

Example:

.. code-block:: python

    @irc3.event(rfc.PONG)
    def myevent(bot):
        # do something

PRIVMSG
-------

Match ``^(@(?P<tags>\S+) )?:(?P<mask>\S+!\S+@\S+) (?P<event>(PRIVMSG|NOTICE)) (?P<target>\S+) :\s*(?P<data>\S+.*)$``

Example:

.. code-block:: python

    @irc3.event(rfc.PRIVMSG)
    def myevent(bot):
        # do something

QUIT
----

Match ``^(@(?P<tags>\S+) )?:(?P<mask>\S+) QUIT(\s+:(?P<data>.*)|$)``

Example:

.. code-block:: python

    @irc3.event(rfc.QUIT)
    def myevent(bot):
        # do something

TOPIC
-----

Match ``^(@(?P<tags>\S+) )?:(?P<mask>\S+!\S+@\S+) TOPIC (?P<channel>\S+) :(?P<data>\S+.*)$``

Example:

.. code-block:: python

    @irc3.event(rfc.TOPIC)
    def myevent(bot):
        # do something

