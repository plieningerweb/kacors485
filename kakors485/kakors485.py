import serial

class KakoRS485Parser(object):
    """
    parse the answer of kakco rs485 protokoll
    """

    mapping = {}
    mapping[0] = {
            0: {'name' : 'last_command_sent',
                'description': 'Adresse & Fernsteuerbefehl'},
            1: {'name': 'status',
                'description': 'Status des Wechselrichters'},
            2: {'name': 'u_dc',
                'description': 'Generator Spannung'},
            3: {'name': 'i_dc',
                'description': 'Generator Strom'},
            4: {'name': 'p_dc',
                'description': 'Generator Leistung'},
            5: {'name': 'u_ac',
                'description': 'Netz Spannung'},
            6: {'name': 'i_ac',
                'description': 'Netz Strom'},
            7: {'name': 'p_ac',
                'description': 'Einspeiseleistung'},
            8: {'name':  'temp',
                'description': 'Geraetetemperatur'},
            9: {'name': 'e_day',
                'description': 'Tagesenergie'},
            10: {'name': 'type',
                'description': 'Wechselrichter Typ'},
            11: {'name': 'checksum',
                'description': 'Pruefsumme'},
        }
    mapping[3] = {
            0: {'name' : 'last_command_sent',
                'description': 'Adresse & Fernsteuerbefehl'},
            1: {'name': 'p_top',
                'description': 'Spitzenleistung in W'},
            2: {'name': 'e_day',
                'description': 'Tagesenergie in Wh'},
            3: {'name': 'no_idea',
                'description': 'Zaehler der Hochzaehlt, ka was'},
            4: {'name': 'e_all',
                'description': 'Gesamtenergie in 0.1kWH'},
            5: {'name': 'counter_h',
                'description': 'Zaehler Stunden'},
            6: {'name': 'run_today',
                'description': 'Betriebsstunden heute in h'},
            7: {'name': 'run_all',
                'description': 'Betriebsstunden gesamt in h'},
            8: {'name': 'checksum',
                'description': 'Pruefsumme'},
        }


    def parse(self,answer):
        #split on any whitespace
        l = answer.split()

        #parse first field
        command = l[0]
        inverterName = command[1:3]
        sentCommand = int(command[-1])

        if not sentCommand in self.mapping:
            raise Exception('unknown command "{}" to parse'.format(sentCommand))

        mymap = self.mapping[sentCommand]

        if len(l) != len(mymap):
            raise Exception('length of answer and template not the same')


        ret = {}
        for i,value in enumerate(l):
            ret[i] = mymap[i]
            ret[i]['value'] = value

        return ret

    def listDictNameToKey(self,l,out={}):
        for i in l:
            out = self.dictNameToKey(i,out)

        return out

    def dictNameToKey(self,d,out={}):
        for k in d:
            item = d[k]
            out[item['name']] = item

        return out




class KakoRS485(object):
    """
    KakoRS485 can talk to kako powador rs485 interface

    supports:
        * reading current values
    """

    waitBeforeRead = 0.3

    def __init__(self,serialPort):
        """
        initalize which serial port we should use

        example
        ``
        kako = KakoRS485('/dev/ttyUSB0')
        ``
        """

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

        answers = []

        newline = '\r\n'

        sendCommands = [0,2,3]
        commands = []
        for s in sendCommands:
            commands.append('#{:02d}{:01d}\r\n'.format(inverterNumber,s))

        for cmd in commands:
            answers.append(self.sendCmdAndRead(cmd))

        return answers

    def readInverterAndParse(self,inverterNumber):
        answers = self.readInverter(inverterNumber)

        P = KakoRS485Parser()

        print("answers",answers)

        parsed = []
        for a in answers:
            if len(a) == 0:
                continue
            if len(a) > 1:
                raise Exception('answer of sent command was more than one line')
            parsed.append(P.parse(a[0]))

        return P.listDictNameToKey(parsed)
            

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

        #wait some time to let device answer
        time.sleep(self.waitBeforeRead)

        #read answer
        #while ser.inWaiting() > 0:
        #    out += ser.read(1)

        #read answer line
        answer = []
        while self.ser.inWaiting() > 0:
            answer.append(self.ser.readline())

        return answer



