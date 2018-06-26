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
from config import Config
from construct.core import ConstructError
from asylog import Asylog

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

        self.logger = Asylog().getLogger()
        self.config = Config()
        self.app_config = self.config.get_app_config()
        self.mod_config =self.config.get_product_config()


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
                tips.print_green(tips.pass_big_font)
            else:
                self.logger.critical("Fail. " + msg)
                #raise AppError("Frequency test Fail")
                tips.print_red(tips.fail_big_font)


class RFTestOfQC30xFxA(RFTest):
    
    def init_ble_module(self): #This is standard init module entry point from legacy implementation.
        self.programmer.init_QC30xFxA()
        #raw_input("CSR module is in normal mode. Press any key")

    def openCSRTestEngine(self):
        ref_ble_port = self.app_config.find(".//interface/ref_ble_port").text
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
        ref_ble_port = self.app_config.find(".//interface/ref_ble_port").text
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
        mod_config = self.config.get_product_config()
        relative_dir = mod_config.find(".//rf_test/testprogram/directory").text
        abs_dir = os.path.join(os.getcwd(), relative_dir)

        print abs_dir
        print psrFile
    
        psrFileFullPath = os.path.join(abs_dir, psrFile)

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
            self.merge_PSR(self.mod_config.find(".//rf_test/crystal_oscillator_error/prePSRfile").text)
            self.csrLib.bccmdSetColdReset(self.csrLib.dutport)  #warm reset to make configurations effective

            #raw_input("Frequency being output")
            freq_port = self.app_config.find(".//interface/freq_counter_port").text
            compensation = int(self.app_config.find(".//frequency_counter/compensation_hz").text)

            high = int(self.mod_config.find(".//rf_test/crystal_oscillator_error/limit/eco1/high").text)
            low = int(self.mod_config.find(".//rf_test/crystal_oscillator_error/limit/eco1/low").text)
            time.sleep(1)
            frequency = int(
                self.mod_config.find(".//rf_test/crystal_oscillator_error/limit/eco1").attrib['frequency_hz'])

            self.frequency(freq_port, low, high, frequency, compensation)

            #find and merge postPSRfile
            self.merge_PSR(self.mod_config.find(".//rf_test/crystal_oscillator_error/postPSRfile").text)

            #find and merge postPSRfile
            #self.merge_PSR(self.mod_config.find(".//rf_test/crystal_oscillator_error/postPSRfile").text)


        finally:
            self.closeCSRTestEngine()

    def  BT_power_test(self):
        print "BT2.1 Power Tests"
        #read all test case parameters here
        freqStr = (self.mod_config.find(".//rf_test/BT21_Power_Test/frequency").text)
        freqList = tuple([int(i.strip()) for i in freqStr.split(',')])
        #print freqList
        intPA = int(self.mod_config.find(".//rf_test/BT21_Power_Test/intPA").text)
        extPA = int(self.mod_config.find(".//rf_test/BT21_Power_Test/extPA").text)
        intmod = int (self.mod_config.find(".//rf_test/BT21_Power_Test/intmod").text)
        sampleSize = int(self.mod_config.find(".//rf_test/BT21_Power_Test/sampleSize").text)
        highlimit = int(self.mod_config.find(".//rf_test/BT21_Power_Test/limit/high").text)
        lowlimit = int(self.mod_config.find(".//rf_test/BT21_Power_Test/limit/low").text)

        try:
            self.openCSRTestEngine()
            for freq in freqList:
                print ("Transmitting frequency carrier at {} MHz".format(freq))
                rssiBuffer = [0] * sampleSize
                self.csrLib.radiotestTxstart(self.csrLib.dutport, freq, intPA, extPA, intmod)
                self.csrLib.radiotestRxstart2(self.csrLib.refport, freq, sampleSize)
                #raw_input("Press any key to start hqGetRSSI")
                rssi = self.csrLib.hqGetRssi(self.csrLib.refport, sampleSize)
                print ("Measured RSSI = {}".format(rssi))
                self.csrLib.radiotestPause(self.csrLib.refport)
                self.csrLib.radiotestPause(self.csrLib.dutport)
                # Determine pass or fail
                msg = "Measured RSSI = {} ({},{}) at {}MHz".format(rssi, lowlimit, highlimit, freq)
                if lowlimit < rssi < highlimit:
                    self.logger.info("Pass. " + msg)
                    tips.print_green(tips.pass_big_font)
                else:
                    self.logger.critical("Fail. " + msg)
                    raise AppError("Frequency test Fail")

        finally:
            self.closeCSRTestEngine()


    def BT_BER_LoopBack_Test(self):
        print "BT2.1 BER Tests using loopback mode"
        #read all test case parameters here
        channelStr = (self.mod_config.find(".//rf_test/BT21_BER_Test/channel").text)
        channelList = tuple([int(i.strip()) for i in channelStr.split(',')])
        for ch in channelList:
            if not (0 <= int(ch) <= 78):
                raise AppError("Test channel {} out of range".format(ch))
        #print ("channelList = {}".format(channelList))
        hopen = int(self.mod_config.find(".//rf_test/BT21_BER_Test/hopen").text)
        msg = "Hopping enable = {}".format(hopen)
        self.logger.info(msg)
        #print ("hopen = {}".format(hopen))
        sampleSize = int(self.mod_config.find(".//rf_test/BT21_BER_Test/sampleSize").text)
        msg = "sampleSize = {}".format(sampleSize)
        self.logger.info(msg)
        #print ("sampleSize = {}".format(sampleSize))
        packetType = self.mod_config.find(".//rf_test/BT21_BER_Test/packet").text
        msg = "packetType = {}".format(packetType)
        self.logger.info(msg)
        
        # Transmit side parameters
        intPA = int(self.mod_config.find(".//rf_test/BT21_BER_Test/tx/intPA").text)
        msg = "intPA = {}".format(intPA)
        self.logger.info(msg)
        #print ("intPA = {}".format(intPA))
        extPA = int(self.mod_config.find(".//rf_test/BT21_BER_Test/tx/extPA").text)
        msg = "extPA = {}".format(extPA)
        self.logger.info(msg)
        #print ("extPA = {}".format(extPA))
        intmod = int(self.mod_config.find(".//rf_test/BT21_BER_Test/tx/intmod").text)
        msg = "intmod = {}".format(intmod)
        self.logger.info(msg)
        #print ("intmod = {}".format(intmod))

        # Receive side parameters
        rx_attenuation = int(self.mod_config.find(".//rf_test/BT21_BER_Test/rx/rx_attenuation").text)
        msg = "rx_attenuation = {}".format(rx_attenuation)
        self.logger.info(msg)
        #print ("rx_attenuation = {}".format(rx_attenuation))

        # Test limt parameters
        ber_high = float (self.mod_config.find(".//rf_test/BT21_BER_Test/limit/ber/high").text)
        ber_low = float (self.mod_config.find(".//rf_test/BT21_BER_Test/limit/ber/low").text)

        try:
            self.openCSRTestEngine()
            #raw_input("BT PER Tests, press any key")
            for ch in channelList:
                print ("Testing loopback BER  at channel {}".format(ch))
                # 1. configure the packet types
                self.csrLib.radiotestCfgPkt(self.csrLib.dutport, packetType)
                self.csrLib.radiotestCfgPkt(self.csrLib.refport, packetType)
                #2. Set the TX/RX interval
                self.csrLib.radiotestCfgFreq(self.csrLib.dutport, 37500, 9375, 1)
                self.csrLib.radiotestCfgFreq(self.csrLib.refport, 37500, 9375, 1)
                #3. Start the transmitter and receiver
                self.csrLib.radiotestBerLoopback(self.csrLib.refport, int(ch)+2402, intPA, extPA, sampleSize)
                self.csrLib.radiotestLoopback(self.csrLib.dutport, int(ch)+2402, intPA, extPA)
                #4. Gather the BER information
                dataBuf = [0]*9  # allocate an 9-element array for BER results
                self.csrLib.hqGetBer(self.csrLib.refport, dataBuf)
                print ("Bit count = {}".format(dataBuf[0]))
                print ("Bit errors = {}".format(dataBuf[1]))
                print ("Received packets = {}".format(dataBuf[3]))
                print ("Expected packets = {}".format(dataBuf[4]))
                print ("Header errors = {}".format(dataBuf[5]))
                print ("CRC errors = {}".format(dataBuf[6]))
                print ("Uncorrected errors  = {}".format(dataBuf[7]))
                print ("Sync errors = {}".format(dataBuf[8]))
                ber = float (dataBuf[1]) / dataBuf[0] * 100
                msg = "Measured %BER = {:4.2f} ({},{}) at channel {}".format(ber, ber_low, ber_high, ch)
                if ber_low <= ber <= ber_high:
                    self.logger.info("Pass. " + msg)
                    tips.print_green(tips.pass_big_font)
                else:
                    self.logger.critical("Fail. " + msg)
                    raise AppError("BT2.1 loopback BER test Fail")
        finally:
            self.closeCSRTestEngine()