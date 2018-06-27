# -*- coding: utf-8 -*-
import subprocess
from helpers import AppError
import color_beep as tips
from asylog import Asylog
from config import Config
import os
name ="Error"
class ProductProgramError(AppError):
    pass

class ProductProgram(object):
    def __init__(self):
        self.config = Config()
        mod_config =self.config.get_product_config()
        relative_dir = mod_config.find(".//program/directory").text
        abs_dir = os.path.join(os.getcwd(),relative_dir)
        firmware = os.path.join(abs_dir,mod_config.find(".//program/firmware").text)
        self.logger = Asylog().getLogger()
        self.cmd_order='burn'
        self.software_path=firmware
        self.logger.info("Software_Name:"+mod_config.find(".//program/firmware").text)


    # -------------------------------------------------------------------------
    # Module Programming Routine
    # -------------------------------------------------------------------------
    def Product_Flashing(self):
        try:
            command = "nvscmd.exe {} {}".format(self.cmd_order, self.software_path)
            subprocess.check_call(command, shell=True)
            self.logger.info('Programming Success')
            
        except Exception:
            self.logger.info('Programming Fail')
            raise ProductProgramError("Platform {} not supported yet".format(name))



if __name__ == '__main__':
    Program_Test = None

    Program_Test = ProductProgram()
    Program_Test.Product_Flashing()






