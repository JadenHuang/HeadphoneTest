from six import with_metaclass
from decimal import Decimal
from construct import Struct, Const, Bytes, Byte
from construct.core import ConstructError
import serial
import re
import time


class FrequencyCounterError(Exception):
    pass


class FrequencyCounter(object):
    def __init__(self, comport):
        self.port = comport
        self.frequency_struct = Struct(
            "unit" / Bytes(2),
            "sign" / Bytes(1),
            "point" / Bytes(1),
            "frequency" / Bytes(8),
        )

    def _xgood_sample(self, max_read_times=5):

        cnt = 0
        while cnt < max_read_times:
            cnt += 1
            try:
                self.port.reset_input_buffer()
                temp = self.port.read(32)
                m = re.search(r'0241(\d{12})', repr(temp))
                if m:
                    return self.frequency_struct.parse(m.group(1))
                else:
                    if cnt >= max_read_times:
                        raise FrequencyCounterError("Can't acquire the right stream, {!r}".format(temp))

            except ConstructError as e:
                if cnt >= max_read_times:
                    raise FrequencyCounterError(e)

    def _good_sample(self, max_read_times=5):
        # need to rewrite this routine
        self.port.reset_input_buffer()
        # search for '0241' pattern for max 2 seconds 
        
        startTime = time.time()
        preambleFound=False
        while (time.time() - startTime) <= 2 :
            if self.port.read(1)=='\x02':
                if self.port.read(1)=='4':
                    if self.port.read(1)=='1':
                        preambleFound=True
                        break

        if not preambleFound:
            raise FrequencyCounterError("Preamble pattern not found from frquency counter")
        
        countStr = self.port.read(12)#Annunciator for Display + Decimal Point(DP),Position from right to the left + Get the Value
        print self.port.read(1)     #Frequency counter Ending code
        return self.frequency_struct.parse(countStr)

        
    def freq(self):
        data = self._good_sample()
        frequency = int(data["frequency"])
        point = int(data["point"])
        sign = int(data["sign"])
        unit = int(data["unit"])
        power = 1

        # MHz to Hz
        if unit == 67:
            power = 1000000
        elif unit == 33:
            power = 1000
        elif unit == 31:
            power = 1
        return float(Decimal(frequency) * (1 + sign * -2) * power) / (10 ** point)


if __name__ == "__main__":
    p = serial.Serial("COM33")
    fc = FrequencyCounter(p)
    print fc.freq()
