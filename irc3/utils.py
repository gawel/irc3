# -*- coding: utf-8 -*-


class IrcString(str):

    @property
    def nick(self):
        if '!' in self:
            return self.split('!', 1)[0]
        if not self.is_channel and not self.is_server:
            return self

    @property
    def lnick(self):
        nick = self.nick
        if nick:
            return nick.lower()

    @property
    def host(self):
        if '!' in self:
            return self.split('!', 1)[1]

    @property
    def is_user(self):
        return '!' in self

    @property
    def is_channel(self):
        return self.startswith(('#', '&'))

    @property
    def is_server(self):
        if self == '*':
            return True
        return '!' not in self and '.' in self

    @property
    def is_nick(self):
        return not (self.is_server or self.is_channel)


class Config(dict):

    def __getattr__(self, attr):
        return self[attr]
