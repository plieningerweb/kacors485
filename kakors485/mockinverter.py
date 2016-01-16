#!/usr/bin/python
# -*- coding: utf-8 -*-

mapping = {
        '#010': '*010 4 585.9 10.17 5958 229.5 24.90 5720 36 17614 9600I dx',
        '#013': '*013 2286 4184 42 581 8:46 11:04 11:04 as',

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

    

