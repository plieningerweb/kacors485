
import serial

class KakoRS485(object):
    """
    KakoRS485 can talk to kako powador rs485 interface

    supports:
        * reading current values
    """

    def __init__(self,serialPort):
        """
        initalize which serial port we should use

        example
        ``
        kako = KakoRS485('/dev/ttyUSB0')
        ``
        """

        self.ser = serial.Serial(
            port=serialPort,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
        )

        ser.open()
        ser.isOpen()

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

        commands = [
            str(inverterNumber) + '1' + newline,
            str(inverterNumber) + '2' + newline,
            str(inverterNumber) + '4' + newline,
                ]

        for cmd in commands:
            answers.append(self.sendCmdAndRead(cmd))

        return answers

    def sendCmdAndRead(self,cmd, wait=0.3):
        """
        send command on rs485 and read answer

        return list of answered lines
        if no answer after waiting time, return empty list 
        """

        #can only send bytearrays
        bytearr = cmd.encode()
        self.ser.write(bytearr)

        #wait some time to let device answer
        time.sleep(wait)

        #read answer
        #while ser.inWaiting() > 0:
        #    out += ser.read(1)

        #read answer line
        answer = []
        while ser.inWaiting() > 0:
            answer.append(self.ser.readline())

        return answer



