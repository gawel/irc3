FROM python:3.4.3

RUN adduser --disabled-password --gecos '' irc3

RUN cd /usr/src && git clone https://github.com/gawel/irc3.git
RUN cd /usr/src/irc3 && pip install ipython && pip install -e .[test]

RUN mkdir -p /usr/src/bot && chown -R irc3:irc3 /usr/src/bot
WORKDIR /usr/src/bot

ONBUILD COPY . /usr/src/bot

USER irc3

CMD ["/usr/local/bin/irc3", "config.ini"]
