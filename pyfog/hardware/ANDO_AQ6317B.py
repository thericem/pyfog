# coding: utf-8

import visa
import numpy as np

class ANDO_AQ6317B:
    """ ANDO AQ6317B Optical Spectrum Analyzer"""
    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)

    def identify(self):
        return self.inst.query('*IDN?')

    def set_timeout(self,milliseconds):
        self.inst.timeout = milliseconds

    def get_spectrum(self):
        spectrum_string = self.inst.query('LDATB')
        spectrum = np.array(spectrum_string[:-2].split(','))
        spectrum = spectrum.astype(np.float)[2:]

        wavelength_string = self.inst.query('WDATB')
        wavelength = np.array(wavelength_string[:-2].split(','))
        wavelength = wavelength.astype(np.float)[2:]

        return spectrum, wavelengthPyDAQmx