#!/usr/bin/python
# -*- coding: utf-8 -*-

mapping = {
        #clean answer, what we whould expect
        '#010': '*010 4 585.9 10.17 5958 229.5 24.90 5720 36 17614 d 9600I',
        '#013': '2286 4184 42 581 8:46 11:04 11:04',

        #recorded answer on system
        '#010': 'n\xd6\xf6V\xeb\x00\n*010   4 585.9  0.88   515 230.0  2.04   460  14    377 x 8000xi\r\x00',
        '#013': 'n\xd6\x96V\xeb\x00\n   883    377  44661  44661      0:47  25301:20  25301:20\x00'
        }

import sys
import serial
port = sys.argv[1]

s = serial.Serial(port)


while True:
    line = s.readline().strip()

    print("line is '{:s}'".format(line))

    if line in mapping:
        print("send answer '{:s}'".format(mapping[line]))
        s.write(mapping[line]+'\r\n')
