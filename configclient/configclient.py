import sys    # for serial port recognition
import os
import tkinter as tk
from tkinter import filedialog
from pygmypossum import PygmyPossum

SERIAL_PORT_NAME = 'COM9'  # TODO add means to change this from menu
COLUMN_WIDTH = 12
RETRN_TO_MENU = "press 'Enter' to return to main menu.."    

def getUsrInput(selection):

    # connect to the device
    pypo = PygmyPossum("COM9")
    
    if selection == "SINGLE":
        while True:
            try:
                usrProgID = int(input("Which usrProgram would you like to edit ? <0:15> "))
                if usrProgID > 15 or usrProgID < 0:
                    print("Value must be between 0 and 15")
                else:
                    break
            except ValueError:
                os.system('cls' if os.name == 'nt' else 'clear') # clear console
                print("!Achtung! This is not a whole number")
        
        printUsrProgHeader()
        userProg = pypo.getUsrProg(usrProgID)
        printUsrProg(usrProgID, userProg)

        print('')
        print("Enter 'E' to edit or ", end='')
        try:
            y = input(RETRN_TO_MENU)
            if(y == 'E'):
                editUsrProg(usrProg)
        except SyntaxError:
            y = None

    elif selection == "ALL":
        printUsrProgHeader()
        for x in range(16):
            userProg = pypo.getUsrProg(x) # grap a UserProg object
            printUsrProg(x, userProg)     # return it
        print('')
        print("Enter 'S' to save to text file or ", end='')
        try:
            y = input(RETRN_TO_MENU)
            if(y == 'S'):
                saveUsrProg()
        except SyntaxError:
            y = None

def saveUsrProg():
    root = tk.Tk()
    root.withdraw()
    f = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    text2save = str("text.get(1.0, END)") # starts from `1.0`, not `0.0`
    f.write(text2save)
    f.close()

###########################################
# print a formatted header
###########################################
def printUsrProgHeader():
    print("{}{}{}{}".format("usrProg".ljust(COLUMN_WIDTH),
                            "numOfSnaps".ljust(COLUMN_WIDTH),
                            "snapPeriod".ljust(COLUMN_WIDTH),
                            "minEventPeriod".ljust(COLUMN_WIDTH)))

###########################################
# make changes to a user program
###########################################
def editUsrProg(usrProg):
    curNumOfSnaps = getUserProg(usrProg)[4]
    curSnapPeriod = getUserProg(usrProg)[6] << 8 | getUserProg(usrProg)[5]
    curMinEventPeriod = getUserProg(usrProg)[7]

    print("You are making changes to usrProg: {}".format(usrProg))
    input("Enter value for numOfSnaps, current value is: {}, new value: ".format(curNumOfSnaps))
    input("Enter value for snapPeriod, current value is: {}ms, new value (ms): ".format(curSnapPeriod))
    input("Enter value for minEventPeriod, current value is: {}s, new value (s): ".format(curMinEventPeriod))

###########################################
# Get list of serial ports
###########################################
def getSerialPorts():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    print("Getting all available serial ports...")
    print("This may take a sec...")

    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
            print(port)
        except (OSError, serial.SerialException):
            pass

    input("Press Enter to Continue..")

###########################################
# get dipswitch values
###########################################
def getDipSwitches():

    ser = serial.Serial(SERIAL_PORT_NAME, 9600, timeout=None,)

    packet = bytearray()
    packet.append(0x50)  # start frame byte
    packet.append(0x44)  # 'D'
    packet.append(0x04)  # end frame byte

    # grab the data from the MCU
    ser.write(packet)
    packet = ser.read(16)
    ser.close()

    for x in packet:
        print("{} ".format(hex(x)), end='')
    print('')

    print("Current DIP switch setting is: {}".format(packet[2]))
    input("Press Enter to Continue..")

###########################################
# sets default values to PygmyPossum
###########################################
def setDefaultValues():

    ser = serial.Serial(SERIAL_PORT_NAME, 9600, timeout=None,)

    packet = bytearray()
    packet.append(0x50)  # start frame byte
    packet.append(0x56)  # 'V'
    packet.append(0x04)  # end frame byte

    # send command packet and store response
    ser.write(packet)
    packet = ser.read(16)
    ser.close()

    for x in packet:
        print(hex(x), end='')
        print(" ", end='')
    print('')

    # print out all values
    getUsrInput("ALL")


def printUsrProg(usrProgID, usrProg):
    print("{}".format(usrProgID).ljust(COLUMN_WIDTH), end='')
    print("{}".format(usrProg.numOfSnaps).ljust(COLUMN_WIDTH), end='')
    print("{}".format(usrProg.snapPeriod).ljust(COLUMN_WIDTH), end='')
    print("{}".format(usrProg.minEventPeriod).ljust(COLUMN_WIDTH), end='')

    print('')  # newline
