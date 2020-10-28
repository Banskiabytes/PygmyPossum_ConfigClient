# imports
import codecs
import serial


# Defining a class
class PygmyPossum:

    # class variables 
    SERIAL_PORT_NAME = ''  # TODO add means to change this from menu
    TIMEOUT = 1 # 1second
    
    def __init__(self, serialPortName):
        self.SERIAL_PORT_NAME = serialPortName
    
    def output(self):
        print(self.SERIAL_PORT_NAME)

    # return the user program
    def getUsrProg(self, usrProgID):
        ser = serial.Serial(self.SERIAL_PORT_NAME, 9600, timeout=self.TIMEOUT,)
        
        packet = bytearray()
        packet.append(0x50)      # start frame byte
        packet.append(0x41)      # 'A' - return user program
        if usrProgID == 0x04:    # escape char
            packet.append(0x7D)  # after esc char
        packet.append(usrProgID) # user Program ID
        packet.append(0x04)      # end frame byte

        ser.write(packet)
        packet = ser.read(16)
        ser.close()

        # strip unnessasary packet data
        usrProgByteArray = bytearray()
        for x in range(8):
            usrProgByteArray.append(packet[x+3])
        
        return UserProg(usrProgByteArray) # return a UserProg object

    def setUsrProg(self, usrProgID, numOfSnaps, snapPeriod, minEventPeriod):
        print("set user prog")


class UserProg:
    numOfSnaps = 0
    snapPeriod = 0
    minEventPeriod = 0

    def __init__(self, usrProgByteArray):
        self.numOfSnaps = usrProgByteArray[1]
        self.snapPeriod = usrProgByteArray[3] << 8 | usrProgByteArray[2]
        self.minEventPeriod = usrProgByteArray[4]


    
        
