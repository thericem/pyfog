# coding: utf-8

import pyvisa

class SRS_SR844:

    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)

