FROM python:3.4.3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ONBUILD COPY requirements.txt /usr/src/app/
ONBUILD RUN pip install irc3[test]

ONBUILD COPY . /usr/src/app
CMD ['irc3', '/usr/src/app/config.ini']
