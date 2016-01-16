#!/bin/bash

python setup.py bdist_wheel


#test only
#python setup.py register -r https://testpypi.python.org/pypi
#twine upload -r pypitest dist/*

#production
#see http://python-packaging-user-guide.readthedocs.org/en/latest/distributing/
twine upload dist/*
