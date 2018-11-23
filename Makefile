APP:=$(shell basename `pwd`)
HOSTNAME:=$(shell hostname)
HOST:=amandine
PYTHON?=$(HOME)/.venvs/py3/bin/python3

build:
	docker build -t gawel/irc3 .

venv:
	 $(PYTHON) -m venv venv
	./venv/bin/pip install -e .[test,web]

run: venv
	./venv/bin/irc3 config.ini

upgrade: venv
ifeq ($(HOSTNAME), $(HOST))
	git pull origin master
	~/apps/bin/circusctl restart $(APP)
else
	git push origin master
	ssh $(HOST) "cd ~/apps/$(APP) && make upgrade"
endif


