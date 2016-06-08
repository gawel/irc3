from irc3.testing import BotTestCase
from irc3.plugins import quakenet


class TestQuakenet(BotTestCase):

    config = dict(
            includes=['irc3.plugins.quakenet'],
            quakenet=dict(user="bot", password="password", hidehost=True,
                          challenge_auth=False))

    def test_challenge(self):
        # Test vectors taken from:
        # https://www.quakenet.org/development/challengeauth
        user1 = ("mooking", "0000000000")
        user2 = ("fishking", "ZZZZZZZZZZ")
        challenge = "12345678901234567890123456789012"

        def digest(user, algo):
            return quakenet.challenge_auth(user[0], user[1], challenge,
                                           str.lower, algo)

        res1 = digest(user1, "md5")
        self.assertEquals(res1, '2ed1a1f1d2cd5487d2e18f27213286b9')

        res2 = digest(user2, "md5")
        self.assertEquals(res2, '8990cb478218b6c0063daf08dd7e1a72')

        res3 = digest(user1, "sha1")
        self.assertEquals(res3, 'd0328d41426bd2ace183467ce0a6305445e3d497')

        res4 = digest(user2, "sha1")
        self.assertEquals(res4, '4de3f1c86dd0f59da44852d507e193c339c4b108')

        res5 = digest(user1, "sha256")
        self.assertEquals(res5, 'f6eced34321a69c270472d06c50e959c48e9fd323'
                          'b2c5d3194f44b50a118a7ea')

        res6 = digest(user2, "sha256")
        self.assertEquals(res6, '504056d53b2fc4fd783dc4f086dabc59f845d201e650'
                          'b96dfa95dacc8cac2892')

    def test_simple_auth(self):
        bot = self.callFTU()
        bot.notify('connection_made')
        bot.dispatch(':azubu.uk.quakenet.org 376 irc3 :End of /MOTD command.')
        self.assertSent(['AUTH bot password', "MODE irc3 +x"])

    def test_challenge_auth(self):
        quakenet_config = dict(self.config["quakenet"])
        quakenet_config["challenge_auth"] = True
        bot = self.callFTU(quakenet=quakenet_config)
        bot.notify('connection_made')
        bot.dispatch(':azubu.uk.quakenet.org 376 irc3 :End of /MOTD command.')
        self.assertSent(['PRIVMSG Q@CServe.quakenet.org :CHALLENGE'])
        bot.dispatch(":Q!TheQBot@CServe.quakenet.org NOTICE irc3 "
                     ":CHALLENGE 12345678901234567890123456789012 "
                     "HMAC-MD5 HMAC-SHA-1 HMAC-SHA-256 LEGACY-MD5")

        self.assertSent(["PRIVMSG Q@CServe.quakenet.org "
                         ":CHALLENGEAUTH bot 76abae4fbbcf56b7296c1477e7d378a"
                         "2590a147cf92afa5a952b321491c51bc6 HMAC-SHA-256"])
