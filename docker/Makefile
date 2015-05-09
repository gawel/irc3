build:
	docker build --rm=true -f Dockerfile -t irc3:latest .

run:
	docker run -v $(PWD)/../:/usr/src/bot -v $(HOME)/.irc3:/home/irc3/.irc3 irc3:latest irc3 examples/dev.ini
