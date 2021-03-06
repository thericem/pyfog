# coding: utf-8
"""Experiment

A wrapper for a PyTables file that contains Gyro runs

"""

import tables as pt
import pandas as pd
import numpy as np
from allantools import oadev
import warnings


class Tombstone(pd.Series):
    """An extension of ``pandas.Series``, which contains raw data from a
    tombstone test.

    Parameters
    ----------
    data : array-like of floats
        The raw data measured in volts from a lock-in amplifier. If no scale
        factor is provided, this data is presumed to be in units of °/h.
    rate : float
        The sampling rate in Hz
    start : float
        The unix time stamp of the start of the run. Used to create the index
        of the Tombstone object. This can be calculated by
        running ``time.time()`` or similar. If no value is passed, the index
        of the Tombstone object will be in hours since start.
    scale_factor : float
        The conversion factor between the lock-in amplifier voltage and deg/h,
        expressed in deg/h/V.

    Attributes
    ----------
    adev : 2-tuple of arrays of floats
        Returns the Allan deviation in degrees/hour in a 2-tuple. The first
        tuple is an array of floats representing the integration times. The
        second tuple is an array of floats representing the allan deviations.
    noise : float
        The calculated angular random walk in units of °/√h taken from the
        1-Hz point on the
        Allan variance curve.
    arw : float
        The calculated angular random walk in units of °/√h taken from the
        1-Hz point on the
        Allan deviation curve.
    drift : float
        The minimum allan deviation in units of °/h.
    """

    def __init__(self, data, rate, start=None, scale_factor=None,
                 *args, **kwargs):

        if start:
            date_index = pd.date_range(
                start=start*1e9, periods=len(data),
                freq='%.3g ms' % (1000/rate), tz='UTC')
            date_index = date_index.tz_convert('America/Los_Angeles')\
                    .tz_localize(None)
        else:
            date_index = np.arange(len(data))/60/60/rate
        super().__init__(data, date_index, *args, **kwargs)
        if scale_factor:
            self.name = 'voltage'
        else:
            self.name = 'rotation'
        self.rate = rate
        self.scale_factor = scale_factor
        self.start = start

    def __finalize__(self, other, method=None, **kwargs):
        return self

    @property
    def _constructor(self):
        return Tombstone

    @property
    def _constructor_sliced(self):
        return Tombstone

    @property
    def voltage(self):
        if self.scale_factor:
            return np.array(self)
        else:
            raise ValueError('Scale Factor not set')

    # Aliases
    v = voltage
    V = voltage
    volt = voltage
    volts = voltage

    @property
    def millivolts(self):
        return self.voltage * 1e3

    @property
    def microvolts(self):
        return self.voltage * 1e6

    @property
    def nanovolts(self):
        return self.voltage * 1e9

    mV = mv = millivolt = millivolts
    uV = uv = microvolt = microvolts
    nV = nv = nanovolt = nanovolts

    @property
    def rotation(self):
        if self.scale_factor:
            return self.scale_factor * np.array(self)
        else:
            return np.array(self)

    @property
    def adev(self):
        tau, dev, _, _ = oadev(self.rotation, rate=self.rate,
                               data_type='freq')
        return tau, dev

    @property
    def noise(self):
        _, dev, _, _ = oadev(self.rotation, rate=self.rate, data_type='freq')
        return dev[0]/60

    # alias
    arw = noise

    @property
    def drift(self):
        tau, dev, _, _ = oadev(self.rotation, rate=self.rate,
                               data_type='freq')
        return min(dev)


class Experiment():
    """ A thin wrapper around an h5 file used for storing Allan Deviation runs

    """
    def __init__(self, filename, read_only=False):

        mode = 'a'  # append
        if read_only:
            mode = 'r'

        self.h5file = pt.open_file(filename, mode=mode)

    def __setitem__(self, key, item):
        key = str(key)
        if 'Tombstone' not in str(type(item)):
            raise ValueError('Object must be type pyfog.Tombstone')
        
        with warnings.catch_warnings(record=False) as w:
            warnings.simplefilter("ignore")
            arr = self.h5file.create_array(self.h5file.root, key, np.array(item))
        arr.attrs.rate = item.rate
        arr.attrs.start = item.start
        arr.attrs.scale_factor = item.scale_factor
        arr.flush()

    def __getitem__(self, key):
        key = str(key)
        arr = self.h5file.get_node('/%s' % key)
        return Tombstone(
            np.array(arr),
            rate=arr.attrs.rate,
            scale_factor=arr.attrs.scale_factor,
            start=arr.attrs.start)

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, key):
        self.h5file.remove_node('/%s' % key)

    def clear(self):
        for key in self.keys():
            self.h5file.remove_node('/%s' % key)

    # TODO
    # def copy(self):
    #    return self.__dict__.copy()

    def has_key(self, k):
        return k in self.keys()

    # TODO
    # def update(self, *args, **kwargs):
    #    return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return [k.name for k in self.h5file.walk_nodes('/', classname='Array')]

    def values(self):
        return [self.__getitem__(k.name) for k in
                self.h5file.walk_nodes('/', classname='Array')]

    def items(self):
        return zip(self.keys(), self.values())

    # TODO
    # def __cmp__(self, dict_):
    #    return self.__cmp__(self.__dict__, dict_)

    def __contains__(self, item):
        return item in self.items()

    def __iter__(self):
        return iter(self.items())

    def close(self):
        return self.h5file.close()
