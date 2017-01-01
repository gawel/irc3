import hashlib
import hmac
import irc3

__doc__ = '''
=================================================
:mod:`irc3.plugins.quakenet` QuakeNet authorization
=================================================

Plugin supports both simple and
`challenge based <https://www.quakenet.org/development/challengeauth>`_
authorization.  Challenge based auth is used by default, since it is more
secure than simple.  Also, plugin can hide your IP after authorization
by applying ``+x`` mode.

..
    >>> from irc3.testing import IrcBot
    >>> from irc3.testing import ini2config

Usage::

    >>> config = ini2config("""
    ... [bot]
    ... includes =
    ...     irc3.plugins.quakenet
    ... [quakenet]
    ... user = login
    ... password = passw
    ... # optional, false by default
    ... hidehost = true
    ... # optional, true by default
    ... challenge_auth = true
    ... """)
    >>> bot = IrcBot(**config)

'''

Q_NICK = "Q@CServe.quakenet.org"
CHALLENGE_PATTERN = ("^:Q![a-zA-Z]+@CServe.quakenet.org NOTICE "
                     "(?P<nick>\S+) :CHALLENGE (?P<challenge>[a-z0-9]+) ")


def get_digest(digest):
    if not isinstance(digest, str):  # pragma: no cover
        raise ValueError("Wrong type of digest")

    digest = digest.lower()
    if digest in ("sha256", "sha1", "md5"):
        return getattr(hashlib, digest)
    else:  # pragma: no cover
        raise ValueError("Wrong value for digest")


def challenge_auth(username, password, challenge, lower, digest='sha256'):
    """Calculates quakenet's challenge auth hash

    .. code-block:: python

        >>> challenge_auth("mooking", "0000000000",
        ...     "12345678901234567890123456789012", str.lower, "md5")
        '2ed1a1f1d2cd5487d2e18f27213286b9'
    """
    def hdig(x):
        return fdigest(x).hexdigest()

    fdigest = get_digest(digest)
    luser = lower(username)
    tpass = password[:10].encode("ascii")
    hvalue = hdig("{0}:{1}".format(luser, hdig(tpass)).encode("ascii"))
    bhvalue = hvalue.encode("ascii")
    bchallenge = challenge.encode("ascii")
    return hmac.HMAC(bhvalue, bchallenge, digestmod=fdigest).hexdigest()


@irc3.plugin
class QuakeNet(object):

    requires = [
        'irc3.plugins.core',
        'irc3.plugins.casefold'
    ]

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config.get("quakenet", {})
        self.user = self.config.get('user', None)
        self.password = self.config.get('password', None)
        self.hidehost = bool(self.config.get('hidehost', False))
        # secure by default
        self.challenge_auth = bool(self.config.get('challenge_auth', True))
        self.pending_auth = False

    def server_ready(self):
        self.auth()

    def auth(self):
        if self.user and self.password:
            if self.challenge_auth:
                self.bot.log.info("Requesting challenge")
                self.bot.privmsg(Q_NICK, 'CHALLENGE')
                self.pending_auth = True
            else:
                self.bot.log.info("Sending login information to QuakeNet")
                self.bot.send_line("AUTH {user} {password}".format(
                                   user=self.user, password=self.password))
                self.after_auth()

    def after_auth(self):
        if self.hidehost:
            self.bot.mode(self.bot.nick, "+x")

    @irc3.event(CHALLENGE_PATTERN)
    def get_challenge(self, nick, challenge, **kwargs):
        if nick == self.bot.nick and self.pending_auth:
            hauth = challenge_auth(self.user, self.password, challenge,
                                   self.bot.casefold, "sha256")
            cmd = 'CHALLENGEAUTH {user} {response} {algo}'. \
                format(user=self.user, response=hauth, algo="HMAC-SHA-256")

            self.bot.log.info("Performing challenge authorization on QuakeNet")
            self.bot.privmsg(Q_NICK, cmd)
            self.after_auth()
