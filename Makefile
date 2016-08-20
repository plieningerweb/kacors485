
.PHONY: test

requirements:
	pip install -r requirements/default.txt

test-requirements: requirements

test-local:
	trial test.test_kacors485

test: test-requirements develop test-local

develop: requirements develop-local

develop-local: uninstall
	python setup.py develop

uninstall:
	python setup.py clean
