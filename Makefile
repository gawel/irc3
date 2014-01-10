clean:
	rm -Rf docs/_build

build:
	bin/parse_rfc
	bin/gen_doc
	bin/irc3 examples/bot.ini --help-page > examples/commands.rst
	cd docs; make html; cd ..

