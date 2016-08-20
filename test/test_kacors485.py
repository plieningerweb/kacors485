import unittest

#set import path to ../ directory
import sys
import os.path
libpath = os.path.abspath(os.path.join(os.path.dirname(__file__),  os.path.pardir))
sys.path.append(libpath)

from kacors485.kacors485 import KacoRS485, KacoRS485Parser

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
        k = KacoRS485('/dev/ttyUSB0')

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
        k = KacoRS485('/dev/ttyUSB0')

        k.close()

        #mock_serial.return_value is the mock of an instance
        #return_value more or less contains the instace when calls is inited
        #here: return_value is a instance of serial.Serial
        mock_serial.return_value.close.assert_called_once_with()

    @mock.patch('serial.Serial', spec=serial.Serial)
    def testSendCmdAndRead(self,mock_serial):
        k = KacoRS485('/dev/ttyUSB0')

        #setup side effect
        self.first_call = True

        instance = mock_serial.return_value
        instance.inWaiting.side_effect = self.side_effect_1_and_then_0
        instance.readline.return_value = 'answer'

        read = k.sendCmdAndRead('question')

        instance.write.assert_called_once_with('question')

        self.assertEqual('answer',read)

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
        with self.assertRaises(Exception):
            KacoRS485('/dev/ttyUSB0notthere*')

        k = KacoRS485('/dev/ttyUSB0')

        #setup side effect
        self.first_call = True

        instance = mock_serial.return_value
        instance.inWaiting.side_effect = self.side_effect_1_and_then_0
        instance.readline.return_value = 'answer'

        nr = 2
        read = k.readInverter(nr)

        expected_calls = [
                    mock.call('#0'+str(nr)+'0\r\n'),
                    #mock.call('#0'+str(nr)+'2\r\n'),
                    mock.call('#0'+str(nr)+'3\r\n'),
                ]

        self.assertEqual(instance.write.mock_calls, expected_calls)

        #we only send once answer back
        expected_answer = {'#020\r\n': 'answer', '#023\r\n': ''}
        self.assertEqual(read,expected_answer)

class TestParserMethods(unittest.TestCase):
    maxDiff = None

    def answer_to_list(self, answer):
        return [answer[k]['value'] for k in answer]

    def testParse0(self):
        p = KacoRS485Parser()

        out = '*010	4	585.9	10.17	5958	229.5	24.90	5720	36	17614	9600I dx'
        expected = ['*010', 4, 585.9, 10.17, 5958, 229.5, 24.90, 5720, 36, 17614, '9600I', 'dx']

        answer = p.parse(out, '#010\r\n')
        self.assertEqual(sorted(self.answer_to_list(answer)),sorted(expected))

    def testParse3(self):
        p = KacoRS485Parser()

        out = '*013 2286 4184 42 581 8:46 11:04 11:04'
        expected = ['*013', 2286, 4184, '42', 581, '8:46', '11:04', '11:04']
        answer = p.parse(out, '#013\r\n')
        self.assertEqual(sorted(self.answer_to_list(answer)),sorted(expected))
