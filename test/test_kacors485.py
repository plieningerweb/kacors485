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
    def testInitialization_Wildcard(self, mock_serial):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        k = KacoRS485(os.path.join(dir_path, 'ttyUSB*'))

        mock_serial.assert_called_once_with(
            port=os.path.join(dir_path, 'ttyUSB0.test'),
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

    test_lines = [
        ('#010\r\n',
         '*010	4	585.9	10.17	5958	229.5	24.90	5720	36	17614	9600I dx',
         ['*010', 4, 585.9, 10.17, 5958, 229.5, 24.90, 5720, 36, 17614, '9600I', 'dx']
        ),
        ('#013\r\n',
         '*013 2286 4184 42 581 8:46 11:04 11:04',
         ['*013', 2286, 4184, '42', 581, '8:46', '11:04', '11:04']
        ),
        #do not answer anything for test cases
        ('#010\r\n',
         '',
         False
        ),
        ('#013\r\n',
         '',
         False
        ),
        ('#010\r\n',
         'n\xd6\xf6V\xeb\x00\n*010   4 585.9  0.88   515 230.0  2.04   460  14    377 x 8000xi\r\x00',
         ['n\xd6\xf6V\xeb*010', 4, 585.9, 0.88, 515.0, 230.0, 2.04, 460.0, 14.0, 377.0, 'x', '8000xi']
        ),
        ('#013\r\n',
         'n\xd6\x96V\xeb\x00\n   883    377  44661  44661      0:47  25301:20  25301:20\x00',
         ['n\xd6\x96V\xeb', 883.0, 377.0, '44661', 44661.0, '0:47', '25301:20', '25301:20']
        ),
        #recorded answer, but intendetly broken! (missing one part)
        ('#013\r\n',
         'n\xd6\x96V\xeb\x00\n   377  44661  44661      0:47  25301:20  25301:20\x00',
         False
        ),
        ('#020\r\n',
         'n\xd6\xf6V\xeb\x00\n*020   4 585.9  0.88   515 230.0  2.04   460  14    377 x 8000xi\r\x00',
         ['n\xd6\xf6V\xeb*020', 4, 585.9, 0.88, 515.0, 230.0, 2.04, 460.0, 14.0, 377.0, 'x', '8000xi']
        ),
        ('#023\r\n',
         'n\xd6\x96V\xeb\x00\n   883    377  44661  44661      0:47  25301:20  25301:20\x00',
         ['n\xd6\x96V\xeb', 883.0, 377.0, '44661', 44661.0, '0:47', '25301:20', '25301:20']
        ),
        ('#010\r\n',
         '*010   4 448.4 12.95  5806 236.5 23.60  5555  50  28143 \xf5 8000xi',
         ['*010', 4, 448.4, 12.95, 5806.0, 236.5, 23.6, 5555.0, 50.0, 28143.0, '\xf5', '8000xi']
        ),
        ('#013\r\n',
         '7911  28144  46176  46176 10:29  27443:01  27443:01',
         [7911.0, 28144.0, '46176', 46176.0, '10:29', '27443:01', '27443:01']
        ),

    ]

    def test_parse(self):
        p = KacoRS485Parser()

        for i, item in enumerate(self.test_lines):
            print("test parse {}".format(i))
            print("try to parse: {}".format(item[1]))
            try:
                answer = p.parse(item[1], item[0])
                print(self.answer_to_list(answer))
                self.assertEqual(sorted(item[2]), sorted(self.answer_to_list(answer)))
            except Exception as e:
                if item[2] is False:
                    # we do not except an answer but exception
                    pass
                else:
                    raise
