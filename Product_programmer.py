import subprocess
from helpers import AppError
import color_beep as tips
name ="Error"
class ProductProgramError():
    pass

class ProductProgram(object):
    def __init__(self):
        self.cmd_order='burn'
        self.software_path='C:\Users\Jaden\Desktop\Production_of_software\BL10_SVN411.XUV'
        print ("Software Path:"+self.software_path)


    # -------------------------------------------------------------------------
    # Module Programming Routine
    # -------------------------------------------------------------------------
    def Product_Flashing(self):
        try:
            command = "nvscmd.exe {} {}".format(self.cmd_order, self.software_path)
            subprocess.check_call(command, shell=True)
            tips.print_green(tips.pass_big_font)
        except Exception:
            tips.print_red(tips.fail_big_font)
            #raise ProductProgramError("Platform {} not supported yet".format(name))




if __name__ == '__main__':
    Program_Test = None

    Program_Test = ProductProgram()
    Program_Test.Product_Flashing()






