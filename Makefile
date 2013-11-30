clean:
	rm -Rf docs/_build

build:
	bin/parse_rfc
	bin/gen_doc
	cd docs; make html; cd ..

