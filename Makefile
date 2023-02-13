#!/usr/bin/make
#
all: run
py:=2.7
plone:=4

.PHONY: bootstrap buildout run test cleanall
bootstrap:
	virtualenv -p python$(py) .
	bin/pip install -r requirements.txt

buildout:
	cp test_plone$(plone).cfg buildout.cfg
	if ! test -f bin/buildout;then make bootstrap;fi
	bin/buildout

run:
	if ! test -f bin/instance;then make buildout;fi
	bin/instance fg

test: buildout
	bin/test

.PHONY: vcr
vcr:  ## Shows requirements in checkversion-r.html
	bin/versioncheck -rbo checkversion-r.html ${cfg}

cleanall:
	rm -fr bin develop-eggs htmlcov include .installed.cfg lib .mr.developer.cfg parts downloads eggs
