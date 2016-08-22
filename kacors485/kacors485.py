# -*- coding: utf-8 -*-
import serial
import glob
import json
import string


class KacoRS485Parser(object):
    """
    parse the answer of kakco rs485 protokoll
    """
    printable = set(string.printable)
    mapping = {}
    mapping[0] = {
#            -1: {'name': 'garbage'},
            0: {'name' : 'last_command_sent',
                'description': 'Adresse & Fernsteuerbefehl'},
            1: {'name': 'status',
                'convert_to': int,
                'description': """Status des Wechselrichters\n
Nicht sicher, aber könnte etwa so sein:
0 Wechselrichter hat sich gerade eingeschaltet Nur nach erstem Einschalten am Morgen
1 Wartemodus. Netz- und Solarspannung testen: Wechselrichter wartet bis die Spannungen
sicher anstehen und mit der Einspeisung begonnen werden kann
2 Warten auf Ausschalten Generatorspannung und -leistung ist zu gering.
Zustand bevor in die Nachtabschaltung übergegangen wird
3 Konstantspannungsregler Beim Einspeisebeginn wird kurzzeitig mit
konstanter Generatorspannung eingespeist (80% der gemessenen Leerlaufspannung)
4 MPP- Regler, ständige Suchbewegung Bei geringer Einstrahlung wird mit suchendem
MPP- Regler eingespeist
5 MPP- Regler, ohne Suchbewegung Bei hoher Einstrahlung wird für maximalen
Ertrag mit patentiertem MPP- Regler eingespeist
9 Fehlersuchbetrieb Bei Auftreten eines internen Fehlers
10 Übertemperaturabschaltung Bei Überhitzung des Wechselrichters
(Kühlkörpertemperatur >80°C) durch ständige Überlastung und fehlende Luftzirkulation,
schaltet sich der Wechselrichter ab. Ursache: Zu großer Solargenerator, zu hohe
Umgebungstemperatur, Wechselrichterdefekt.
11 Leistungsbegrenzung Schutzfunktion des Wechselrichters, wenn zu viel Generatorleistung geliefert wird oder der
Kühlkörper des Gerätes heißer als 65°C wurde
12 Überlastabschaltung Schutzfunktion des Wechselrichters, wenn zu
viel Generatorleistung geliefert wird
13 Überspannungsabschaltung Schutzfunktion des Wechselrichters, wenn Netzspannung zu hoch ist
14 Netzausfall (3-phasige Überwachung) Schutzfunktion des Wechselrichters, wenn eine
der drei Netzphasen ausgefallen ist oder die Spannung außerhalb der Toleranz ist.
15 Übergang zur Nachtabschaltung Wechselrichter legt sich schlafen
"""               },
            2: {'name': 'u_dc',
                'convert_to': float,
                'description': 'Generator Spannung in V *10'},
            3: {'name': 'i_dc',
                'convert_to': float,
                'description': 'Generator Strom in A 100'},
            4: {'name': 'p_dc',
                'convert_to': float,
                'description': 'Generator Leistung in W'},
            5: {'name': 'u_ac',
                'convert_to': float,
                'description': 'Netz Spannung in V *10'},
            6: {'name': 'i_ac',
                'convert_to': float,
                'description': 'Netz Strom in A *100'},
            7: {'name': 'p_ac',
                'convert_to': float,
                'description': 'Einspeiseleistung in W'},
            8: {'name':  'temp',
                'convert_to': float,
                'description': 'Geraetetemperatur in °C'},
            9: {'name': 'e_day',
                'convert_to': float,
                'description': 'Tagesenergie in Wh'},
            10: {'name': 'checksum',
                'description': 'Pruefsumme'},
            11: {'name': 'type',
                'description': 'Wechselrichter Typ'},
        }
    mapping[3] = {
            0: {'name' : 'last_command_sent',
                'description': 'Adresse & Fernsteuerbefehl'},
            1: {'name': 'p_top',
                'convert_to': float,
                'description': 'Spitzenleistung in W'},
            2: {'name': 'e_day',
                'convert_to': float,
                'description': 'Tagesenergie in Wh'},
            3: {'name': 'no_idea',
                'description': 'Zaehler der Hochzaehlt, ka was, evlt auch Gesamtenergie in kWh'},
            4: {'name': 'e_all',
                'convert_to': float,
                'description': 'Gesamtenergie in kWh'},
            5: {'name': 'run_today',
                'description': 'Betriebsstunden heute in hh:mm'},
            6: {'name': 'run_all',
                'description': 'Betriebsstunden gesamt in h:mm'},
            7: {'name': 'run_all_again',
                'description': 'Betriebsstunden gesamt, evtl Zaehler in h:mm'},
#            8: {'name': 'checksum',
#                'description': 'Pruefsumme'},
        }


    def parse(self,answer,command):
        #split on any whitespace
        answer = answer.replace('\r','').replace('\x00','').replace('\n','')
        l = answer.split()

        #parse first field
        sentCommand = int(command[-3])

        if not sentCommand in self.mapping:
            raise Exception('unknown command "{}" to parse in {:s}'.format(sentCommand, repr(answer)))

        # fix: copy if we remove an item
        mymap = self.mapping[sentCommand].copy()

        if len(l) == 1 and sentCommand == 3:
            #some inverters do not have a command 3
            #they only have command one
            #do not throw an exception, just do not return the stuff
            return {}

        # if one less long, assume command is missing:
        if len(l) == (len(mymap) -1):
            # remove last command sent
            print("assume command_sent is missing in answer")
            del mymap[0]
            # rearrange keys, lower each key by one
            mymap = {(key-1): mymap[key] for key in mymap}

        if len(l) != len(mymap):
            print("input",l,"len",len(l))
            print("map",mymap,"len",len(mymap))
            raise Exception('length of answer and template not the same: {:s}'.format(repr(answer)))

        ret = {}
        for i,value in enumerate(l):
            if 'convert_to' in mymap[i]:
                value = mymap[i]['convert_to'](value)

            try:
                json.dumps(value)
            except Exception:
                value = self.convert_to_printable(value)

            ret[i] = mymap[i]
            ret[i]['value'] = value

        return ret

    def convert_to_printable(self, value):
        return filter(lambda x: x in self.printable, value)

    def listDictNameToKey(self,l,out={}):
        for i in l:
            out = self.dictNameToKey(i,out)

        return out

    def dictNameToKey(self,d,out={}):
        for k in d:
            item = d[k]
            out[item['name']] = item

        return out




class KacoRS485(object):
    """
    KacoRS485 can talk to kaco powador rs485 interface

    supports:
        * reading current values
    """

    waitBeforeRead = 0.7

    def port_from_wildcard(self, port):
        port = glob.glob(port)
        if not port:
            raise Exception('could not find a valid rs485 port')
        return port[0]

    def __init__(self,serialPort):
        """
        initalize which serial port we should use

        example
        ``
        kaco = KacoRS485('/dev/ttyUSB0')
        ``
        """
        if '*' in serialPort:
            serialPort = self.port_from_wildcard(serialPort)

        #create and open serial port
        self.ser = serial.Serial(
            port=serialPort,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
        )

    def close(self):
        """
        close serial connection
        """
        self.ser.close()

    def readInverter(self,inverterNumber):
        """
        read all available data from inverter inverterNumber

        inverterNumber: can be between 0 and 32
        """

        answers = {}

        sendCommands = [0,3]
        commands = []
        for s in sendCommands:
            commands.append('#{:02d}{:01d}\r\n'.format(inverterNumber,s))

        for cmd in commands:
            answers[cmd] = self.sendCmdAndRead(cmd)

        return answers

    def readInverterAndParse(self,inverterNumber):
        answers = self.readInverter(inverterNumber)

        P = KacoRS485Parser()

        print("answers",answers)

        parsed = []
        for k in answers:
            item = answers[k]
            if len(item) == 0:
                continue
            parsed.append(P.parse(item,k))

        #all answers could be empty, what should we do?
        #we could also silently answer an empty dict
        #but we prefer to raise an exception
        if len(parsed) <= 0:
            raise Exception('Could not get an answer from the inverter number {}; Answer: {:s}'.format(inverterNumber, repr(answers)))

        #important, set input to empty dict
        #otherwise, we will reuse input from last function call
        return P.listDictNameToKey(parsed,{})


    def sendCmdAndRead(self,cmd):
        import time
        """
        send command on rs485 and read answer

        return list of answered lines
        if no answer after waiting time, return empty list
        """

        #can only send bytearrays
        bytearr = cmd.encode()
        self.ser.write(bytearr)

        print("send to rs485",bytearr)

        #wait some time to let device answer
        time.sleep(self.waitBeforeRead)

        #read answer
        #while ser.inWaiting() > 0:
        #    out += ser.read(1)

        #read answer line
        answer = []
        while self.ser.inWaiting() > 0:
            answer.append(self.ser.readline())

        return ''.join(answer)
