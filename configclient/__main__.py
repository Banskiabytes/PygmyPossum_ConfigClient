from consolemenu import *
from consolemenu.format import *
from consolemenu.items import *
import configclient

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

    PYPO_GETUSRPROG_ONE = ["SINGLE"]
    PYPO_GETUSRPROG_ALL = ["ALL"]

    # Menu items will call functions
    function_getAllUsrProgs    = FunctionItem("Read all user programs", configclient.getUsrInput, args=PYPO_GETUSRPROG_ALL)   
    function_setUsrProg        = FunctionItem("Edit user program", configclient.getUsrInput, args=PYPO_GETUSRPROG_ONE)
    function_getDipSwitches    = FunctionItem("Get dip switches", configclient.getDipSwitches)
    function_getSerialPorts    = FunctionItem("Get serial ports", configclient.getSerialPorts)
    function_setDeviceDefaults = FunctionItem("Set device defaults", configclient.setDefaultValues)

    # Add all the items to the root menu
    menu.append_item(function_getAllUsrProgs)
    menu.append_item(function_setUsrProg)
    menu.append_item(function_getDipSwitches)
    menu.append_item(function_getSerialPorts)
    menu.append_item(function_setDeviceDefaults)

    # Show the menu
    menu.start()
    menu.join()

if __name__ == "__main__":
    main()
