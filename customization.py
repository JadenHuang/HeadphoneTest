# -*- coding: utf-8 -*-
from six import with_metaclass
from collections import Counter
#from .helpers import AppError
from helpers import AppError, Singleton
from global_settings import g
from CSRAPI import CSRSPIDevice 
import time
from asylog import Asylog
import color_beep as tips


class CustomizationError(AppError):
    pass


class Customization(with_metaclass(Singleton, object)):

    def __init__(self):

        self.g = g()
        self.csrlib = CSRSPIDevice()
        self.logger = Asylog().getLogger()
        #self.programmer = programmer.Programmer()

        # End __init__
        # -------------------------------------------------------------------------

    def init_csr_module(self):
        #self.programmer.init_QC30xFxA()
        pass

    def writeSerial(self):
        try:
            self.init_csr_module()
            self.csrLib = CSRSPIDevice()
            print ("Opening SPI port for DUT")
            self.csrLib.openTestEngineSpi()
            self.csrLib.dutport = self.csrLib.spiHandle

            print "Writing CSR BDADDR... "
            nap = int(self.g.serial[0:4], 16)
            uap = int(self.g.serial[4:6], 16)
            lap = int(self.g.serial[6:12], 16)
            print nap, uap, lap
            self.csrlib.psWriteBdAddr(self.csrLib.dutport, lap, uap, nap)
            self.csrLib.closeTestEngine(self.csrLib.dutport)
            self.csrLib.dutport = 0

            print ("Closing SPI port for DUT")    
            self.csrLib.spiHandle = 0
            
            msg = "DUT BDADDR : {}".format(self.g.serial)
            print (msg)
            self.logger.info(msg)
            self.logger.info('Write CSR BDADDR Success')
            self.IncrementSerial()

        except Exception:
            self.logger.info('Write CSR BDADDR Fail')
            tips.print_red(tips.fail_big_font)
            #raise CustomizationError("Platform {} not supported yet".format(name))
            


    def IncrementSerial(self):     
        self.g.serial = "{:012x}".format(int(self.g.serial, 16) + 1)

class CustomizationOfCSRA64215(Customization):
    
    def Run(self):
        self.writeSerial()
