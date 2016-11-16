import visa
import serial
import re

class GPIB:
    def __init__(self, init_scan = True):
        self.resources = []
        self.rm = visa.ResourceManager()
        if init_scan:
            self.scan_resources(self)

    def scan_resources(self, timeout = 1000):
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
        return self.resources

    def lookup(self, lookup_string, index = False):
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
                return matches[0]
            if len(matches) > 1:
                raise Exception('Multiple devices match. Try including parameter index="all"')
        elif index.lower() == "all":
            return matches
        elif isinstance(index, int):
            if len(matches) - 1 >= index:
                return matches[index]
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