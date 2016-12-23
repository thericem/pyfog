import visa

class Agilent_33250A():
    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)

    def identify(self):
        return self.inst.query('*IDN?')

    @property
    def freq(self):
        """Returns frequency in Hz"""

        # get f in kHz
        f = self.inst.query('FREQ?')

        return float(f) * 1e3

    @freq.setter
    def freq(self, val):
        """Sets frequency in Hz"""
        self.inst.write('FREQ %i' %  (val/1000))

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