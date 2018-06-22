# -*- coding: utf-8 -*-
from six import with_metaclass
import time
from decimal import Decimal
from serial import Serial
from abc import abstractmethod, ABCMeta
import color_beep as tips
import subprocess
import os
import msvcrt
import sys

#from asylog import Asylog
#from ModuleTest_Tool.rf_lib.hci_function import HCI
from helpers import AppError, Singleton
import frequency_counter
from CSRAPI import *
#from comminterface import *

class RFTestError(AppError):
    pass


class RFTest(object):
    def __init__(self):
        #self.logger = Asylog().getLogger()


        # self.ref_comport = None
        # self.dut_comport = None
        # self.freq_comport = None
        self.spectrum_analyzer = None

    def frequency(self, freq_comport, low_limit, high_limit, frequency, compensation=0):
        with Serial(freq_comport, baudrate=9600, timeout=1) as freq_comport:
            fc = frequency_counter.FrequencyCounter(freq_comport)
            freq = fc.freq()
            print "read {}, test {}".format(freq, frequency)
            offset = freq - frequency + compensation
            msg = "Frequency_offset = {}Hz ({},{}) in {}kHz eco".format(offset, low_limit, high_limit, frequency / 1000)
            if low_limit < offset < high_limit:
                self.logger.info("Pass. " + msg)
            else:
               # self.logger.critical("Fail. " + msg)
                #raise AppError("Frequency test Fail")
                tips.print_red(tips.fail_big_font)


class RFTestOfQC30xFxA(RFTest):
    
    def init_ble_module(self): #This is standard init module entry point from legacy implementation.
        self.programmer.init_QC30xFxA()
        #raw_input("CSR module is in normal mode. Press any key")

    def openCSRTestEngine(self):
        ref_ble_port = "COM8"
        #dut_ble_port = "SPI"
        
        self.csrLib = CSRSPIDevice()
        #open DUT SPI port
        print ("Opening SPI port for DUT")
        self.csrLib.openTestEngineSpi()
        self.csrLib.dutport = self.csrLib.spiHandle

        #open REF port
        print ("Opening COM port for REF")
        self.csrLib.openTestEngineCOM(ref_ble_port)
        self.csrLib.refport = self.csrLib.comHandle
            
    def closeCSRTestEngine(self):
        ref_ble_port = "COM3"
        #dut_ble_port = "SPI"

        #close DUT SPI port
        self.csrLib.closeTestEngine(self.csrLib.dutport)
        print ("Closing test engine SPI port for DUT")
        self.csrLib.dutport =0
        self.csrLib.spiHandle = 0

        #close REF SPI port
        self.csrLib.closeTestEngine(self.csrLib.refport)
        print ("Closing test engine COM port for REF")
        self.csrLib.refport =0
        self.csrLib.comHandle = 0

    def merge_PSR(self, psrFile):
        if psrFile == "": 
            return
        #create full path for psrFile
    
        psrFileFullPath = psrFile

        if os.path.isfile(psrFileFullPath):
            self.csrLib.merge_CSR_pscli(self.csrLib.dutport, psrFileFullPath)
        else:
            raise RFTestError ("{} not exist".format(psrFile))


    def frequency_test(self):
        print "Frequency tests"
        #self.init_ble_module()

        try:
            #raw_input("Press any key to start merging PSR")
            self.openCSRTestEngine()
            #find and merge prePSRfile
            self.merge_PSR("C:\Users\Jaden\Desktop\Production_of_software\BL20.psr")
            #self.csrLib.bccmdSetColdReset()  #warm reset to make configurations effective

            #raw_input("Frequency being output")
            freq_port = "COM7"
            compensation = 0

            high = 15
            low = -15
            time.sleep(1)
            frequency = 1000000

            self.frequency(freq_port, low, high, frequency, compensation)

            #find and merge postPSRfile
            #self.merge_PSR(self.mod_config.find(".//rf_test/crystal_oscillator_error/postPSRfile").text)

        finally:
            self.closeCSRTestEngine()