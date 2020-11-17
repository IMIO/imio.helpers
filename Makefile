#!/usr/bin/make
#
all: run
py:=2.7
plone:=4

.PHONY: bootstrap buildout run test cleanall
bootstrap:
	if command -v virtualenv-2.7 >/dev/null 2>&1 ; then virtualenv-2.7 .;else virtualenv -p python$(py) .;fi
	bin/pip install -r requirements.txt
	./bin/python bootstrap.py --version=2.13.2

buildout:
	cp test_plone$(plone).cfg buildout.cfg
	if ! test -f bin/buildout;then make bootstrap;fi
	bin/buildout

run:
	if ! test -f bin/instance;then make buildout;fi
	bin/instance fg

test: buildout
	bin/test

cleanall:
	rm -fr bin develop-eggs htmlcov include .installed.cfg lib .mr.developer.cfg parts downloads eggs
