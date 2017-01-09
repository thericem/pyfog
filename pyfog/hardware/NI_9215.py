"""
NI 9215
=======

.. module:: NI_9215
   :platform: Unix, Windows
   :synopsis: NI 9215 DAQ Unit Wrapper

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>

This module provides support for the `NI 9215`_ Data Acquisition Unit.
Much of the code base was adapted from examples at <https://pythonhosted.org/PyDAQmx/>.
It is my understanding that the examples make use of C code, so if you have questions
on what specific methods do inside of my code, please search for the documentation
on NI, as they have much more documentation than I do.

.. _NI 9215: https://sine.ni.com/nips/cds/view/p/lang/en/nid/208793

"""

from PyDAQmx import *
import numpy

class NI_9215:
    def __init__(self):
        pass

    def read(self,seconds=1,frequency=10000.0, max_voltage=10,timeout=0):
        """
        Return data from the DAQ.

        Parameters
        ----------
        seconds : int, float
            Sample duration in seconds
        frequency : int, float
            Number of samples to collect per second
        max_voltage : float
            Scale factor. The DAQ expects a range of voltages ranging from -10V
            to +10V. The max_voltage tells ``read()`` what to scale a 10V signal
            by.
        timeout : int, float
            Amount of time after which the program should timeout and give up
            on collecting data.

            - 0 (default) - calculate the timeout based on duration and sample rate
            - -1 - do not time out.
            - other - the timeout


        Returns
        -------
        numpy.array
            A one-dimensional numpy array of the data.
        """
        sample_size = int(seconds * frequency)
        if timeout == 0:
            timeout = seconds
        # Declaration of variable passed by reference
        taskHandle = TaskHandle()
        read = int32()
        self.data = numpy.zeros((sample_size,), dtype=numpy.float64)

        try:
            # DAQmx Configure Code
            DAQmxCreateTask("", byref(taskHandle))
            DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai0", "", DAQmx_Val_Cfg_Default, -10, 10, DAQmx_Val_Volts,
                                     None)
            DAQmxCfgSampClkTiming(taskHandle, "", frequency, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, sample_size)
            # DAQmx Start Code
            DAQmxStartTask(taskHandle)

            # DAQmx Read Code
            DAQmxReadAnalogF64(taskHandle, sample_size, timeout, DAQmx_Val_GroupByChannel, self.data, sample_size, byref(read), None)

            #print("Acquired %d points" % read.value)
        except DAQError as err:
            print("DAQmx Error: %s" % err)
        finally:
            if taskHandle:
                # DAQmx Stop Code
                DAQmxStopTask(taskHandle)
                DAQmxClearTask(taskHandle)

        #TODO clean this up
        self.data = self.data/10 * max_voltage
        return self.data

    def identify(self):
        buf = ctypes.create_string_buffer(16)
        DAQmxGetDevProductType("Dev1", buf, 16);
        return "".join([(c).decode() for c in buf][:-1])
