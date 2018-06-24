# -*- coding: utf-8 -*-
import subprocess
from helpers import AppError
import color_beep as tips
from asylog import Asylog
from config import Config
import os
name ="Error"
class RFProgramError():
    pass

class RFProgram(object):
    def __init__(self):
        self.config = Config()
        mod_config =self.config.get_product_config()
        relative_dir = mod_config.find(".//rf_test/testprogram/directory").text
        abs_dir = os.path.join(os.getcwd(),relative_dir)
        firmware = os.path.join(abs_dir,mod_config.find(".//rf_test/testprogram/firmware").text)
        self.logger = Asylog().getLogger()
        self.cmd_order='burn'
        self.software_path=firmware
        print ("Software Path:"+self.software_path)


    # -------------------------------------------------------------------------
    # Module Programming Routine
    # -------------------------------------------------------------------------
    def RF_Flashing(self):
        try:
            command = "nvscmd.exe {} {}".format(self.cmd_order, self.software_path)
            subprocess.check_call(command, shell=True)
            self.logger.info('Programming Success')
            tips.print_green(tips.pass_big_font)
            
        except Exception:
            self.logger.info('Programming Fail')
            tips.print_red(tips.fail_big_font)
            #raise ProductProgramError("Platform {} not supported yet".format(name))




if __name__ == '__main__':
    Program_Test = None

    Program_Test = RFProgram()
    Program_Test.RF_Flashing()






