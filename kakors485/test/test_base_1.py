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

    def setupMockRead(self,mock_serial,value):
        """
        prepare mock serial to read some data
        it will set the side effect of the inWaiting() function
        in order to exactly read one line
        """
        k = KakoRS485('/dev/ttyUSB0')


        #setup side effect
        self.first_call = True

        instance = mock_serial.return_value
        instance.inWaiting.side_effect = self.side_effect_1_and_then_0

        return k

    @mock.patch('serial.Serial', spec=serial.Serial)
    def testSendCmdAndRead(self,mock_serial):
        k = self.setupMockRead(mock_serial)

        read = k.sendCmdAndRead('test')



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



"""
    def test_upper(self):
  self.assertEqual('foo'.upper(), 'FOO')

def test_isupper(self):
  self.assertTrue('FOO'.isupper())
  self.assertFalse('Foo'.isupper())

def test_split(self):
  s = 'hello world'
  self.assertEqual(s.split(), ['hello', 'world'])
  # check that s.split fails when the separator is not a string
  with self.assertRaises(TypeError):
      s.split(2)

if __name__ == '__main__':
    unittest.main()

     def setUp(self):
                 self.widget = Widget('The widget')

                     def tearDown(self):
                                 self.widget.dispose()
                                         self.widget = None
"""
