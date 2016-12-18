# coding: utf-8
"""
Stanford Research Systems SR844 Lock-In Amplifier
=================================================


"""

import visa

class SRS_SR844:

    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)

        self._sensitivity_dict = {
            0: {"Vrms": 100e-9, "dBm": -127},
            1: {"Vrms": 300e-9, "dBm": -117},
            2: {"Vrms": 1e-6, "dBm": -107},
            3: {"Vrms": 3e-6, "dBm": -97},
            4: {"Vrms": 10e-6, "dBm": -87},
            5: {"Vrms": 30e-6, "dBm": -77},
            6: {"Vrms": 100e-6, "dBm": -67},
            7: {"Vrms": 300e-6, "dBm": -57},
            8: {"Vrms": 1e-3, "dBm": -47},
            9: {"Vrms": 3e-3, "dBm": -37},
            10: {"Vrms": 10e-3, "dBm": -27},
            11: {"Vrms": 30e-3, "dBm": -17},
            12: {"Vrms": 100e-3, "dBm": -7},
            13: {"Vrms": 300e-3, "dBm": 3},
            14: {"Vrms": 1, "dBm": 13},
        }

    def identify(self):
        return self.inst.query('*IDN?')

    @property
    def phase(self):
        return float(self.inst.query('PHAS?')[:-1])

    @phase.setter
    def phase(self, val):
        """The PHAS command sets or queries the detection phase, in degrees, relative to the
    reference. The parameter x is the phase (real number of degrees) and may be
    specified from –360 ≤ x ≤ 360. The value specified is rounded to 0.01° and
    adjusted to the interval [-179.99 , 180.00 ]."""
        self.inst.write('PHAS %f' % val)

    @property
    def sensitivity(self):
        key = int(self.inst.query('SENS?'))
        return self._sensitivity_dict[key]['Vrms']

    @sensitivity.setter
    def sensitivity(self, val):
        key = [d['Vrms'] for d in self._sensitivity_dict.values()].index(val)
        self.inst.write('SENS %i' % key)

    def autophase(self):
        """The APHS command performs the Auto Phase function. This command is the same
as pressing Shift−Phase. This command adjusts the reference phase so that the
current measurement has a Y value of zero and an X value equal to the signal
magnitude, R."""
        self.inst.write('APHS')