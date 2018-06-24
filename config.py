# -*- coding: utf-8 -*-
from six import with_metaclass
import xml.etree.ElementTree as ET
from helpers import Singleton


class Config(with_metaclass(Singleton, object)):
    def __init__(self):
        self.app_tree = ET.parse("./config/config.xml")
        self.product = self.app_tree.find(".//product").text
        self.mod_tree = ET.parse("./config/{}.xml".format(self.product))
        self.platform = self.mod_tree.getroot().attrib["platform"].upper()
        #print self.platform

    def get_product_config(self):

        return self.mod_tree

    def get_app_config(self):

        return self.app_tree

    def get_product_name(self):

        return self.product

    def get_debug_enable(self):
        if self.app_tree.find(".//debug").text == '1':
            return True
        else:
            return False

    def get_product_platform(self):
        return self.platform

    def test_repeat_count(self):
        return int(self.app_tree.find(".//test_case/test_repeat/count").text)

    def test_repeat_stop_at_fail(self):
        return int(self.app_tree.find(".//test_case/test_repeat/stop_at_fail").text)

    def test_repeat_RX_TX_Fail_Count(self):
        return int(self.app_tree.find(".//test_case/test_repeat/RX_TX_Fail_Count").text)
