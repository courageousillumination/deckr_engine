all:
test: reports
	nosetests --with-coverage --cover-package=deckr --cover-branches --cover-html --cover-html-dir=reports/coverage --with-xunit --xunit-file=reports/unittests.xml
reports:
	mkdir -p reports
lint:
	autopep8 --in-place --aggressive --recursive deckr tests
	pylint deckr tests
