"""
NSC-A1 Wrapper
==============

.. module:: NSC_A1
   :platform: Unix, Windows
   :synopsis: NSC-A1 Single Axis USB Stepper Motor Controller

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>

This module provide support for the `NSC-A1`_ Single Axis USB Stepper Motor
Controller.

The stepper motor is a USB to Serial interface. On Windows, you communicate with
it over a COM port, where on Unix, you would communicate over a /dev/tt port.

.. _NSC-A1: http://www.newmarksystems.com/motion-controllers/nsc-a1/

"""

import serial
from msvcrt import getch
import threading
import time
import sys


class NSC_A1:
    def __init__(self, port='COM3', channel=1, timeout=0.1, max_x=10e4,
                 min_x=-10e4, verbose=False):
        """

        Parameters
        ----------
        port: string
            The serial port over which to communicate with the device. On Windows,
        channel: int
            Multiple axes can be controlled by the motor controller. Which
            channel is this rotational stage talking on?
        timeout: float
            How many seconds should the serial interface wait for a response
            before timing out?
        max_x: int, float
            The maximum x (in ticks) to rotate to. There are 10,000 ticks in
            one degree. Rotations beyond this bound will not occur and will
            raise exceptions
        min_x: int, float
            The minimum x (in ticks) to rotate to. There are 10,000 ticks in
            one degree.
        verbose: bool
            If verbose is ``True``, then a progress bar will show while
            the stage is rotating.

        """
        self.verbose = verbose
        self.channel = channel
        self.inst = serial.Serial(port)
        self.inst.timeout = timeout
        self._max_x = max_x
        self._min_x = min_x
        self._max_angle = max_x / 1e4
        self._min_angle = min_x / 1e4

    def cmd(self, command):
        """Send a command to the motor driver over the serial interface

        Parameters
        ----------
        command: basestring
            The command to send to the motor driver. It is padded with the
            channel and carriage return, then converted to bytes, and sent
            over the serial interface.

        Returns
        -------
        bytearray
            The raw response from the serial interface. This can be cast into
            numbers or strings depending on the nature of the data.
        """
        formatted_command = "@{:02d}{}\r".format(self.channel, command)
        self.inst.write(formatted_command.encode())
        return self.inst.read(10)

    def check_range(self, timeout=10):
        def cmd(self, command):
            """An interactive program to check the range of motion of the
            rotation platform.

            The user is prompted for a keyboard interrupt to begin rotation.
            The program then runs to the maximum safe rotation angle
            ``self.max_angle`` and then to the minimum safe rotation angle
            ``self.min_angle``. The user can abort the check at any time by
            throwing a keyboard interrupt.

            Parameters
            ----------
            timeout: int, float
                The amount of time to wait for a keyboard interrupt before
                beginning. We assume the user knows how to use a keyboard
                interrupt, but we check before we rotate the stage.

            Returns
            -------
            None
                If the program returns None, then it completed the full
                rotation without exceptions. If the user throws a keyboard
                interrupt during execution, it is because there was a problem.

            Raises
            ------
            Exception
                If the user does not send a keyboard interrupt during the
                initial timeout phase, the program will assume the user got
                stuck and didn't know how to send a keyboard interrupt. This
                will raise an ``Exception``
            KeyboardInterrupt
                After the rotation has started, if the user raises a
                ``KeyboardInterrupt`` the rotation stage will stop, and
                a KeyboardInterrupt will be raised.
            """


        print("Throw a keyboard interrupt (Ctrl-C) to begin")
        try:
            for i in range(timeout):
                time.sleep(1)
            raise Exception("Timed out!")
        except KeyboardInterrupt:
            print("Let's begin")
            pass

        print("Rotating to {}".format(self.max_x))
        self.x = (self.max_x)

        print("Rotating to {}".format(self.min_x))
        self.x = (self.min_x)

    @property
    def x(self):
        return int(self.cmd('PX'))

    @property
    def angle(self):
        return int(self.cmd('PX')) / 1e4

    @property
    def max_x(self):
        return self._max_x

    @property
    def min_x(self):
        return self._min_x

    @property
    def max_angle(self):
        return self._max_angle

    @property
    def min_angle(self):
        return self._min_angle

    @max_x.setter
    def max_x(self, val):
        self._max_x = val
        self._max_angle = val / 1e4

    @min_x.setter
    def min_x(self, val):
        self._min_x = val
        self._min_angle = val / 1e4

    @max_angle.setter
    def max_angle(self, val):
        self._max_x = val * 1e4
        self._max_angle = val

    @min_angle.setter
    def min_angle(self, val):
        self._min_x = val * 1e4
        self._min_angle = val

    @x.setter
    def x(self, val, unit="ticks"):
        start = self.x
        ticks = self.get_ticks(val, unit)
        if not self.is_safe(ticks):
            return

        self.cmd('ABS')
        self.cmd('X{}'.format(ticks))
        return self.wait_until_motor_is_idle(start, stop=ticks)

    @angle.setter
    def angle(self, val):
        start = self.x
        ticks = self.get_ticks(val, 'deg')
        if not self.is_safe(ticks):
            return
        self.cmd('ABS')
        self.cmd('X{}'.format(ticks))
        return self.wait_until_motor_is_idle(start, stop=ticks)

    def cw(self, val, foreground=True, unit="deg"):
        val = self.get_ticks(val, unit)
        if not self.is_safe(self.x + val):
            return

        self.cmd('INC')
        self.cmd('X{}'.format(val))

        if foreground:
            self.wait_until_motor_is_idle()

    def ccw(self, val, foreground=True, unit="deg"):
        self.cw(-val, foreground, unit)

    def close(self):
        self.inst.close()

    def disconnect(self):
        self.close()

    def is_safe(self, destination_in_ticks):
        if destination_in_ticks > self.max_x or destination_in_ticks < self.min_x:
            # return False
            raise Exception('Rotating that far is too dangerous!')
        return True

    def get_ticks(self, val, unit):
        if unit in ['deg', 'degree', 'degrees']:
            return val * 1e4
        elif unit in ['tick', 'ticks']:
            return val
        else:
            raise Exception("I don't understand your unit {}".format(unit))

    def wait_until_motor_is_idle(self, start=False, stop=False):
        try:
            while True:
                if int(self.cmd('MST')) == 0:
                    if self.verbose and start and stop:
                        sys.stdout.write(
                            "\r                                          ")
                        sys.stdout.write('\r')
                    return True
                if self.verbose and start and stop:
                    # show progress
                    sys.stdout.write('\r')
                    percent = 100 * (self.x - start) / (stop - start)
                    sys.stdout.write(
                        "[%-20s] %d%%" % ('=' * int(percent / 5), percent))
        except KeyboardInterrupt:
            self.cmd('STOP')
            raise KeyboardInterrupt
