import sys    # for serial port recognition
import os
import tkinter as tk
from tkinter import filedialog
from pygmypossum import PygmyPossum
import codecs
import serial

SERIAL_PORT_NAME = 'COM6'  # TODO add means to change this from menu
COLUMN_WIDTH = 12
RETRN_TO_MENU = "press 'Enter' to return to main menu.."    

def getUsrInput(selection):

    # connect to the device
    pypo = PygmyPossum(SERIAL_PORT_NAME)
    
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
                editUsrProg(usrProgID)
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

###########################################
# save usr program to csv
###########################################
def saveUsrProg():
    root = tk.Tk()
    root.withdraw()

    f = filedialog.asksaveasfile(mode='w', initialfile="pygmypossum.config.csv", filetypes = (("CSV files","*.csv"),("all files","*.*")))
    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return

    text2save = "ID,NUM_OF_SNAPS,SNAP_PERIOD_(ms),MIN_EVENT_PERIOD_(s)\n"
    f.write(text2save)

    # connect to the device
    pypo = PygmyPossum(SERIAL_PORT_NAME)

    for x in range(16):
        userProg = pypo.getUsrProg(x) # grap a UserProg object
        text2save = str("{},{},{},{}\n".format(x,
                                userProg.numOfSnaps,
                                userProg.snapPeriod,
                                userProg.minEventPeriod)) # starts from `1.0`, not `0.0`
        f.write(text2save)
    f.close()

def printLinuxQuestion():
    print("Do you want to continue? [Y/n]")

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
def editUsrProg(usrProgID):
    pypo = PygmyPossum(SERIAL_PORT_NAME) # connect to device

    curNumOfSnaps = pypo.getUsrProg(usrProgID).numOfSnaps
    curSnapPeriod = pypo.getUsrProg(usrProgID).snapPeriod
    curMinEventPeriod = pypo.getUsrProg(usrProgID).minEventPeriod

    print("You are making changes to usrProg: {}".format(usrProgID))
    newNumOfSnaps = int(input("Enter value for numOfSnaps, current value is: {}, new value: ".format(curNumOfSnaps)))
    newSnapPeriod = int(input("Enter value for snapPeriod, current value is: {}ms, new value (ms): ".format(curSnapPeriod)))
    newMinEventPeriod = int(input("Enter value for minEventPeriod, current value is: {}s, new value (s): ".format(curMinEventPeriod)))

    # convert the integers (variable width) to bytes
    newSnapPeriodMSB,newSnapPeriodLSB = newSnapPeriod.to_bytes(2, 'big')

    # build the packet to send to device
    # shuold put this in some sort of loop to clean up the escape chars
    packet = bytearray()
    packet.append(0x50)                   # start frame byte
    packet.append(0x42)                   # 'B'
    packet.append(0x7D)                   # Escape Character - send this before a '0x04'
    packet.append(usrProgID)              # 
    packet.append(0x7D)                   # Escape Character - send this before a '0x04'
    packet.append(newNumOfSnaps)          #
    packet.append(0x7D)                   # Escape Character - send this before a '0x04'
    packet.append(newSnapPeriodLSB)       # 
    packet.append(0x7D)                   # Escape Character - send this before a '0x04'
    packet.append(newSnapPeriodMSB)       # 
    packet.append(0x7D)                   # Escape Character - send this before a '0x04'
    packet.append(newMinEventPeriod)      # 
    packet.append(0xFF)                   # spare
    packet.append(0xFF)                   # spare
    packet.append(0xFF)                   # spare
    packet.append(0x04)                   # end frame byte

    ser = serial.Serial(SERIAL_PORT_NAME, 9600, timeout=None,)

    # grab the data from the MCU
    ser.write(packet)
    packet = ser.read(16)
    ser.close()

    for x in packet:
        print("{} ".format(hex(x)), end='')
    print('')

    input("Press Enter to Continue..")

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
# get battery voltage
###########################################
def getBattVoltage():

    ser = serial.Serial(SERIAL_PORT_NAME, 9600, timeout=None,)

    packet = bytearray()
    packet.append(0x50)  # start frame byte
    packet.append(0x45)  # 'E'
    packet.append(0x04)  # end frame byte

    # grab the data from the MCU
    ser.write(packet)
    packet = ser.read(16)
    ser.close()

    for x in packet:
        print("{} ".format(hex(x)), end='')
    print('')

    print("Current battery voltage is: {} {}".format(packet[2],packet[3]))
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
