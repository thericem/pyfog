"""
GPIB
====

.. module:: Instrumentation
   :platform: Windows
   :synopsis: Provides wrappers for Serial and GPIB interfaces

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>

This module provides wrappers for Serial and GPIB interfaces. They can be
instantiated as follows:

>>> import pyfog
>>> gpib = pyfog.instrumentation.GPIB()
>>> ser = pyfog.instrumentation.Serial()

Then using these objects, a user can search for connected interfaces with
much more ease than having to guess and type in commands each time. For
example, to hook up a lock-in amplifier

>>> import pyfog
>>> gpib = pyfog.instrumentation.GPIB()
>>> lia = pyfog.SRS_SR844(gpib.lookup('SR844')['id'])
"""


import visa
import serial
import re

class GPIB:
    """ A wrapper class for the GPIB bus.

    The class also caches connected devices (optionally scanning when
    initiated using the `init_scan` option). This allows one to find devices
    quickly.

    Attributes
    ----------
    resources : list
        A list of tuples. Each tuple contains first the device's response
        to a `*IDN?` query, and second the address of the device on the
        bus.

    """
    def __init__(self, init_scan = True):
        """Initiates the GPIB class.

        Parameters
        ----------
        init_scan : boolean
            If `init_scan` is set to True, then GPIB takes some time to scan
            for all connected GPIB interfaces and stores these interfaces in
            a cache.

        Returns
        -------
        None
        """
        self.resources = []
        self.rm = visa.ResourceManager()
        if init_scan:
            self.scan_resources()

    def scan_resources(self):
        """Scans for any GPIB interfaces connected to the bus.

        Populates `self.resources` with a list of tuples, each tuple
        containing the device's response to an `*IDN?` query and the address
        of the device on the GPIB bus.

        Returns
        -------
        list
            A list of tuples. Each tuple contains first the device's response
            to a `*IDN?` query, and second the address of the device on the
            bus.
        """
        self.resources = []
        for inst_string in self.rm.list_resources():
            try:
                inst = self.rm.open_resource(inst_string)
                idn = inst.query('*IDN?')
                self.resources.append((inst_string,idn))
            except:
                pass
        return self.resources

    def get_resources(self):
        """Returns the cache of resources.

        Returns
        -------
        list
            A list of tuples. Each tuple contains first the device's response
            to a `*IDN?` query, and second the address of the device on the
            bus.
        """
        return self.resources

    def lookup(self, lookup_string, index = False):
        """Returns matches in the device cache for the lookup_string.

        Parameters
        ----------
        lookup_string : basestring
            A regular expression used to query for the device.
        index : int, basestring
            By default, index is set to `False`, which asks the wrapper to
            return only the first matched interface.

            If index is an int,
            it will ask for the nth matched device (0 indexed) to be returned.

            If index is set to `"all"`, then it will return a list of
            dictionaries.


        Returns
        -------
        basestring
            Returns the address on the bus

        .. note::
           If index is set to "all" then this method returns a list of
           dictionaries.

        """

        if len(self.resources) == 0:
            self.scan_resources(self)
            if (len(self.resources) == 0):
                raise Exception('No devices have responded')
        matches = []
        for (inst_string, idn) in self.resources:
            if re.search(lookup_string, idn):
                matches.append({"id" : inst_string, "idn": idn})
        if index == False:
            if len(matches) == 0:
                raise Exception('No devices match search query "{}"'.format(lookup_string))
            elif len(matches) == 1:
                return matches[0]['id']
            if len(matches) > 1:
                raise Exception('Multiple devices match. Try including parameter index="all"')
        elif index.lower() == "all":
            return matches
        elif isinstance(index, int):
            if len(matches) - 1 >= index:
                return matches[index]['id']
            if len(matches) - 1 < index:
                raise Exception('There are not {} matches'.format(index))
        else:
            raise Exception('No behavior set for index={}'.format(index))

class Serial:

    def __init__(self):
        pass

    # http: // stackoverflow.com / questions / 12090503 / listing - available - com - ports -with-python
    def serial_ports():
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    if __name__ == '__main__':
        print(serial_ports())