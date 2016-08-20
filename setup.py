# -*- coding: utf-8 -*-

version = '1.0.3'

import os
import io
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

dependencies = [
    'pyserial'
]


#def read(filename):
#    return open(os.path.join(os.path.dirname(__file__), filename)).read()

def read(*names, **kwargs):
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()

setup(
    name="kacors485",
    version=version,
    author="Andreas Plieninger",
    author_email="info@andreasplieninger.com",
    url="https://github.com/plieningerweb/kacors485",
    description="Python library to retrive and parse information from kaco inverters over serial interface",
    packages=['kacors485'],
    long_description='',
    include_package_data=True,
    install_requires=dependencies,
    license = "GNU GPLv3",
    classifiers=[
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
    ],
)
