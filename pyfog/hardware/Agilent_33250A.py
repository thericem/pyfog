import visa
import numpy as np


class Agilent_33250A():
    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)

    def identify(self):
        return self.inst.query('*IDN?')[:-1]

    @property
    def freq(self):
        """Returns frequency in Hz"""

        # get f in kHz
        f = self.inst.query('FREQ?')

        return float(f)

    @freq.setter
    def freq(self, val):
        """Sets frequency in Hz"""
        self.inst.write('FREQ %i' % val)

    # alias
    frequency = freq

    @property
    def volt(self):
        """Returns Vpp in volts"""
        return float(self.inst.query('VOLT?'))

    @volt.setter
    def volt(self, val):
        """Sets Vpp in volts"""
        # debug
        string = 'VOLT %f' % float(val)
        self.inst.write(string)

    # alias
    voltage = volt

    @property
    def waveform(self):
        wf = self.inst.query('FUNC?')[:-1]
        if wf == 'USER':
            return 'USER ' + self.inst.query('FUNC:USER?')[:-1]
        return wf

    @waveform.setter
    def waveform(self, val):
        waveform_list = [
            'SIN', 'SQU', 'RAMP', 'PULS', 'NOIS', 'DC', 'USER'
        ]
        if val.upper() in (waveform_list):
            return self.inst.write('FUNC %s' % val)

        elif val.upper()[0:4] == 'USER':
            return self.inst.write('FUNC:%s' % val)
        else:
            raise Exception('%s is not a recognized waveform' % val)

    def upload(self, points_array):
        points_array = np.array(points_array)
        if points_array.dtype not in ['float64', 'int32']:
            raise Exception('Array is not numeric')
        if max(points_array) > 1 or min(points_array) < -1:
            raise Exception('Values should be floats between -1 and +1')
        values = ', '.join(map(str, points_array))
        self.inst.write('DATA VOLATILE, %s' % values)

    def save_as(self, waveform_name):
        self.inst.write('DATA:COPY %s' % waveform_name)

    def upload_as(self, points_array, waveform_name):
        self.upload(points_array)
        self.save_as(waveform_name)
