all:
test:
	nosetests
lint:
	autopep8 --in-place --aggressive --recursive deckr tests
	pylint deckr tests
