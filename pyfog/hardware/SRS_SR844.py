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

        # see page 115 of manual
        self._time_constant_list = [ # query by index
            100e-6,
            300e-6,
            1e-3,
            3e-3,
            10e-3,
            30e-3,
            100e-3,
            300e-3,
            1,
            3,
            10,
            30,
            100,
            300,
            1e3,
            3e3,
            10e3,
            30e3
        ]

        # see page 134 of SR844 manual
        self._status_dictionary = {
            0: {"name": "ULK", "set_when": "A reference unlock is detected"},
            1: {"name": "FRQ",
                "set_when": "The reference frequency is out of range"},
            2: {"name": "-", "set_when": "Unused"},
            3: {"name": "TRG", "set_when": "Data storage is triggered"},
            4: {"name": "INP", "set_when": "The signal input overloads"},
            5: {"name": "RSV", "set_when": "The IF amplifier overloads"},
            6: {"name": "FLT", "set_when": "A time constant filter overloads"},
            7: {"name": "CHG",
                "set_when": "Reference frequency changed by more than 1%"},
            8: {"name": "CH1", "set_when": "Channel 1 display or output overloads"},
            9: {"name": "CH2", "set_when": "Channel 2 display or output overloads"},
            10: {"name": "OAX", "set_when": "Either Aux input overloads"},
            11: {"name": "UAX", "set_when": "Ratio input underflows"},
            12: {"name": "-", "set_when": "Unused"},
            13: {"name": "-", "set_when": "Unused"},
            14: {"name": "-", "set_when": "Unused"},
            15: {"name": "-", "set_when": "Unused"},
        }

    def identify(self):
        return self.inst.query('*IDN?')[:-1]

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

    @property
    def time_constant(self):
        key = int(self.inst.query('OFLT?'))
        return self._time_constant_list[key]

    @time_constant.setter
    def time_constant(self, val):
        key = self._time_constant_list.index(val)
        self.inst.write('OFLT %i' % key)

    def autophase(self):
        """The APHS command performs the Auto Phase function. This command is the same
as pressing Shift−Phase. This command adjusts the reference phase so that the
current measurement has a Y value of zero and an X value equal to the signal
magnitude, R."""
        self.inst.write('APHS')

    def autogain(self):
            self.inst.write('AGAN')
            _old_timeout = self.inst.timeout
            self.inst.timeout = 15e3
            while int(self.inst.query('*STB?1')[:-1]):
                # Do nothing until the status bit is clear
                pass
            self.inst.timeout = _old_timeout


    def get_status(self, status = None, verbose=False):
        if status == None:
            status = int(self.inst.query('LIAS?')[:-1])
        else:
            verbose = True
        status_bits = format(status, '016b')

        if not verbose:
            return status_bits

        for idx in range(len(status_bits)):
            if status_bits[idx] == '0':
                continue
            print("{name}:\t{set_when}".format(**self._status_dictionary[idx]))

        return status_bits