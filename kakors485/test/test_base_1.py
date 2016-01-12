import unittest
from kakors485 import KakoRS485

try:
    from unittest import mock
except ImportError:
    import mock

import serial

class TestStringMethods(unittest.TestCase):
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

        mock_serial.return_value.open.assert_called_once_with()

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
                    mock.call(str(nr)+'1\r\n'), 
                    mock.call(str(nr)+'2\r\n'), 
                    mock.call(str(nr)+'4\r\n'), 
                ]

        self.assertTrue(instance.write.mock_calls == expected_calls) 

        #we only send once answer back
        expected_answer = [
                ['answer'],
                [],
                []]
        self.assertEqual(read,expected_answer)
