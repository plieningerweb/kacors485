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

from kacors485 import kacors485


K = kacors485.KacoRS485(port)

K.waitBeforeRead = waitBeforeRead

print('read data from inverter {}'.format(inverterNumber))
import pprint
import json

try:
    data = K.readInverterAndParse(inverterNumber)
except Exception as e:
    import traceback
    trace = traceback.format_exc()
    print("we got an exception")
    pprint.pprint(trace)
    print("now same in json")
    pprint.pprint(json.dumps(trace))
    exit()

K.close()



print('data is')


pprint.pprint(data)

pprint.pprint(json.dumps(data))
