#!/usr/bin/python
# -*- coding: utf-8 -*-


inverterNumber = 1

#wait seconds before reading data
waitBeforeRead = 2

import sys

def showHelp():
    print("usage: example.py serial-port")
    print("e.g.\texample.py /dev/ttyUSB0")
    print("")

if len(sys.argv) != 2:
    showHelp()
    raise Exception('not enough input arguments')

port = sys.argv[1]

import kakors485


K = kakors485.KakoRS485(port)

K.waitBeforeRead = waitBeforeRead

data = K.readInverterAndParse(inverterNumber)

K.close()

print('read data from inverter {}'.format(inverterNumber))

print('data is')

import pprint

pprint.pprint(data)
