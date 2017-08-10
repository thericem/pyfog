# coding: utf-8
"""Methods for simulating FOG performance in an aircraft with perfect
accelerometers.
"""


import numpy as np


def square_pulse(points,
                 duty_cycle=.5,
                 rise_time_over_cycle_time=0,
                 fall_time_over_cycle_time=0):
    """
    Generates square wave cycle, starting at 0 and rising to 1, then falling to
    -1, then rising back to 0 again. The falling slew passes through zero at
    index = duty_cycle * points.

    .. note:: While this cycle runs in O(n) time, the constant is quite large
       due to all the `if`, `elif` and `else` statements the program has to
       execute.
       Better runtimes should be
       possible. If you are using this in an inner loop,
       you may consider optimizing the algithm.

    Parameters
    ----------

    points: int
        The number of points to return in the square pulse
    duty_cycle: float
        A value between 0 and 1, expressing the duty cycle of the square pulse.
    rise_time_over_cycle_time: float
        A value between 0 and 1, expressing what percentage of the cycle time
        the signal is slewing upwards.
    fall_time_over_cycle_time: float
        A value between 0 and 1, expressing what percentage of the cycle time
        the signal is slewing downwards.

    Returns
    -------

    ndarray.float
        An array of values between -1 and 1 representing a single cycle of a
        square wave.


    """

    time = np.linspace(0, 1, points, endpoint=False)

    def get_height_at_progress(ratio):
        if ratio == 0:
            return .5 if rise_time_over_cycle_time else 1
        elif ratio == duty_cycle:
            return .5 if fall_time_over_cycle_time else 0
        elif ratio > 0 and ratio <= rise_time_over_cycle_time / 2:
            return ratio / rise_time_over_cycle_time + .5
        elif (ratio > rise_time_over_cycle_time / 2
              and ratio <= duty_cycle - fall_time_over_cycle_time / 2):
            return 1
        elif (ratio > duty_cycle - fall_time_over_cycle_time / 2
              and ratio <= duty_cycle + fall_time_over_cycle_time / 2):
            return 1 - (
                       ratio - duty_cycle + fall_time_over_cycle_time / 2) / \
                       fall_time_over_cycle_time
        elif (ratio > duty_cycle + fall_time_over_cycle_time / 2
              and ratio <= 1 - rise_time_over_cycle_time / 2):
            return 0
        else:
            return ((
                   ratio - 1 + rise_time_over_cycle_time / 2)
                   / rise_time_over_cycle_time)

    def normalize(ratio):
        v = 2 * get_height_at_progress(ratio) - 1
        if v > 1:
            return 1
        if v < -1:
            return -1
        return v

    return np.array([normalize(t) for t in time])
