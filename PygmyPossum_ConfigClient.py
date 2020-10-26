import sys
from consolemenu import *
from consolemenu.format import *
from consolemenu.items import *
import serial
import codecs

serialPortName = 'COM9'

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
# get all settings
###########################################
def printAllSettings():

    ser = serial.Serial(serialPortName, 9600, timeout=None,)

    for x in range(16):
        packet = bytearray()
        packet.append(0x50) # start frame byte
        packet.append(0x41) # 'A' cmd to get usrProgs
        if x == 0x04:
            packet.append(0x7D) # afterEsc character
        packet.append(x) # usrProg
        packet.append(0x04) # end frame byte

        ser.write(packet)

        packet = ser.read(16)
        for byte in packet:
            print("{} ".format(hex(byte)), end = '')
        print('')

    ser.close()
    print('')
    input("Press Enter to Continue..")

###########################################
# sets default values to PygmyPossum
###########################################
def getDipSwitches():

    ser = serial.Serial(serialPortName, 9600, timeout=None,)

    packet = bytearray()
    packet.append(0x50) # start frame byte
    packet.append(0x44) # 'D'
    packet.append(0x04) # end frame byte

    # grab the data from the MCU
    ser.write(packet)
    packet = ser.read(16)
    ser.close()

    for x in packet:
        print("{} ".format(hex(x)),end = '')
    print('')

    print("Current DIP switch setting is: {}".format(packet[2]))
    input("Press Enter to Continue..")

###########################################
# sets default values to PygmyPossum
###########################################
def setDefaultValues():

    ser = serial.Serial(serialPortName, 9600, timeout=None,)

    packet = bytearray()
    packet.append(0x50) # start frame byte
    packet.append(0x56) # 'V'
    packet.append(0x04) # end frame byte

    ser.write(packet)

    packet = ser.read(16)
    for x in packet:
        print(hex(x), end = '')
        print(" ", end = '')
    print('')

    ser.close()
    printAllSettings()

###########################################
# sets default values to PygmyPossum
###########################################
def getUserProg(**kwargs):

    ser = serial.Serial(serialPortName, 9600, timeout=None,)

    while True:
        try:
            userProg = int(input("Which usrProgram would you like to modify ? <0:15> "))
            if userProg > 15 or userProg < 0:
                print("Value must be between 0 and 15")
            else:
                break
        except ValueError:
            print("This is not a whole number")

    packet = bytearray()
    packet.append(0x50) # start frame byte
    packet.append(0x41) # 'A'
    if userProg == 0x04:
        packet.append(0x7D) # usrProg1
    packet.append(userProg) # usrProg1
    packet.append(0x04) # end frame byte

    ser.write(packet)

    packet = ser.read(16)
    for x in packet:
        print(hex(x), end = '')
        print(" ", end = '')
    print('')

    print("=== Package Number {} ===".format(packet[2]))
    print("Number of Snaps: {} ".format(packet[4]))

    snapPeriod = (packet[6]<<8) | packet[5]
    print("Snap Period (ms): {} ".format(snapPeriod))
    print("Minimum Event Period (s): {} ".format(packet[7]))

    ser.close()
    input("Press Enter to Continue..")

def main():
    # Change some menu formatting
    menu_format = MenuFormatBuilder().set_border_style_type(MenuBorderStyleType.HEAVY_BORDER) \
        .set_prompt("SELECT>") \
        .set_title_align('center') \
        .set_subtitle_align('center') \
        .set_left_margin(4) \
        .set_right_margin(4) \
        .show_header_bottom_border(True) \
        .show_prologue_bottom_border(True) \
        .show_prologue_top_border(True) \
        .set_border_style_type(MenuBorderStyleType.DOUBLE_LINE_BORDER)

    prologue_txt="Welcome to the pygmy possum configuration app. Use your keyboard to navigate the menu settings below."
    epilogue_txt=""
    menu = ConsoleMenu("*** Pygmy Possum ***", "Configuration App", prologue_text=prologue_txt, formatter=menu_format)

    # Menu items will call functions
    function_getAllUsrProgs= FunctionItem("Read all user programs", printAllSettings)
    function_getUsrProg= FunctionItem("Read user program", getUserProg)
    function_getDipSwitches = FunctionItem("Get dip switches", getDipSwitches)
    function_getSerialPorts = FunctionItem("Get serial ports", getSerialPorts)
    function_setDeviceDefaults = FunctionItem("Set device defaults", setDefaultValues)

    # Add all the items to the root menu
    menu.append_item(function_getDipSwitches)
    menu.append_item(function_getAllUsrProgs)
    menu.append_item(function_getUsrProg)
    menu.append_item(function_getSerialPorts)
    menu.append_item(function_setDeviceDefaults)

    # Show the menu
    menu.start()
    menu.join()

if __name__ == "__main__":
    main()
