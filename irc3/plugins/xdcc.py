import sys
import os
import irc3

@irc3.plugin
class XDCC:

    def __init__(self, context=None):
        self.context = context
