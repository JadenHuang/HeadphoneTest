# -*- coding: utf-8 -*-
from six import with_metaclass
from collections import Counter
#from .helpers import AppError
from helpers import AppError, Singleton
from global_settings import g
from CSRAPI import CSRSPIDevice 
import time


class CustomizationError(AppError):
    pass


class Customization(with_metaclass(Singleton, object)):

    def __init__(self):

        self.g = g()
        self.csrlib = CSRSPIDevice()
        #self.programmer = programmer.Programmer()

        # End __init__
        # -------------------------------------------------------------------------

    def init_csr_module(self):
        #self.programmer.init_QC30xFxA()
        pass

    def writeSerial(self):
        
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
        #self.logger.info(msg)
        self.IncrementSerial()
            


    def IncrementSerial(self):     
        self.g.serial = "{:012x}".format(int(self.g.serial, 16) + 1)

class CustomizationOfQC30xFxA(Customization):
    
    def Run(self):
        self.writeSerial()
