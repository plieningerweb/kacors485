import unittest
from kakors485 import KakoRS485, KakoRS485Parser

try:
    from unittest import mock
except ImportError:
    import mock

import serial

class TestSerialMethods(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    @mock.patch('serial.Serial', spec=serial.Serial)
    def testInitialization(self, mock_serial):
        k = KakoRS485('/dev/ttyUSB0')

        mock_serial.assert_called_once_with(
            port='/dev/ttyUSB0', 
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
        )

    @mock.patch('serial.Serial', spec=serial.Serial)
    def testClose(self,mock_serial):
        k = KakoRS485('/dev/ttyUSB0')

        k.close()

        #mock_serial.return_value is the mock of an instance
        #return_value more or less contains the instace when calls is inited
        #here: return_value is a instance of serial.Serial
        mock_serial.return_value.close.assert_called_once_with()

    @mock.patch('serial.Serial', spec=serial.Serial)
    def testSendCmdAndRead(self,mock_serial):
        k = KakoRS485('/dev/ttyUSB0')

        #setup side effect
        self.first_call = True

        instance = mock_serial.return_value
        instance.inWaiting.side_effect = self.side_effect_1_and_then_0
        instance.readline.return_value = 'answer'

        read = k.sendCmdAndRead('question')

        instance.write.assert_called_once_with('question')

        self.assertEqual(['answer'],read)

    def side_effect_1_and_then_0(self):
        """
        side effect
        on first call return 1
        on other calls return 0
        """
        if self.first_call:
            self.first_call = False
            return 1

        return 0

    @mock.patch('serial.Serial', spec=serial.Serial)
    def testReadInverter(self,mock_serial):
        k = KakoRS485('/dev/ttyUSB0')

        #setup side effect
        self.first_call = True

        instance = mock_serial.return_value
        instance.inWaiting.side_effect = self.side_effect_1_and_then_0
        instance.readline.return_value = 'answer'

        nr = 2
        read = k.readInverter(nr)

        expected_calls = [
                    mock.call('#0'+str(nr)+'0\r\n'), 
                    mock.call('#0'+str(nr)+'2\r\n'), 
                    mock.call('#0'+str(nr)+'3\r\n'), 
                ]

        self.assertTrue(instance.write.mock_calls == expected_calls) 

        #we only send once answer back
        expected_answer = [
                ['answer'],
                [],
                []]
        self.assertEqual(read,expected_answer)

class TestParserMethods(unittest.TestCase):

    def testParse0(self):
        p = KakoRS485Parser()

        out = '*010	4	585.9	10.17	5958	229.5	24.90	5720	36	17614	9600I dx'
        expected = {
            0: {'name': 'last_command_sent', 'value': '*010',
                'description': 'Adresse & Fernsteuerbefehl'},
            1: {'name': 'status', 'value': '4',
                'description': 'Status des Wechselrichters'},
            2: {'name': 'u_dc', 'value': '585.9',
                'description': 'Generator Spannung'},
            3: {'name': 'i_dc', 'value': '10.17',
                'description': 'Generator Strom'},
            4: {'name': 'p_dc', 'value': '5958',
                'description': 'Generator Leistung'},
            5: {'name': 'u_ac', 'value': '229.5',
                'description': 'Netz Spannung'},
            6: {'name': 'i_ac', 'value': '24.90', 'description': 'Netz Strom'},
            7: {'name': 'p_ac', 'value': '5720',
                'description': 'Einspeiseleistung'},
            8: {'name': 'temp', 'value': '36',
                'description': 'Geraetetemperatur'},
            9: {'name': 'e_day', 'value': '17614',
                'description': 'Tagesenergie'},
            10: {'name': 'type', 'value': '9600I',
                 'description': 'Wechselrichter Typ'},
            11: {'name': 'checksum', 'value': 'dx',
                 'description': 'Pruefsumme'},
            }

        answer = p.parse(out)

        self.assertEqual(answer,expected)

    def testParse3(self):
        p = KakoRS485Parser()

        out = '*013 2286 4184 42 581 8:46 11:04 11:04 df'
        expected = {
            0: {'name': 'last_command_sent', 'value': '*013',
                'description': 'Adresse & Fernsteuerbefehl'},
            1: {'name': 'p_top', 'value': '2286',
                'description': 'Spitzenleistung in W'},
            2: {'name': 'e_day', 'value': '4184',
                'description': 'Tagesenergie in Wh'},
            3: {'name': 'no_idea', 'value': '42',
                'description': 'Zaehler der Hochzaehlt, ka was'},
            4: {'name': 'e_all', 'value': '581',
                'description': 'Gesamtenergie in 0.1kWH'},
            5: {'name': 'counter_h', 'value': '8:46',
                'description': 'Zaehler Stunden'},
            6: {'name': 'run_today', 'value': '11:04',
                'description': 'Betriebsstunden heute in h'},
            7: {'name': 'run_all', 'value': '11:04',
                'description': 'Betriebsstunden gesamt in h'},
            8: {'name': 'checksum', 'value': 'df',
                'description': 'Pruefsumme'},
            }

        answer = p.parse(out)

        self.assertEqual(answer,expected)


