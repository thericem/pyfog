# coding: utf-8
"""Various code for running
some files
and line breaks
"""

import numpy as np

def generate_fog_data(
        rate=1,  # Hz
        seconds=0,
        minutes=0,
        hours=0,
        arw=0,  # degree/√h
        drift=0  # degree/h
        ):
    """Generates a random fog run based on input time and statistics.

    .. note: Atleast one of `seconds`, `minutes`, or `hours` must be positive,
       otherwise a `ValueError` will be raised.

    Parameters
    ----------
    rate: float, optional
        The number of samples per second.
    seconds: int, optional
        The number of seconds of data
    minutes: int, optional
        The number of minutes to be added to the seconds parameter
    hours: int, optional
        The number of hours to be added to the seconds parameter
    arw: float, optional
        The angular random walk, specified in degrees per root hour
    drift: float, optional
        The bias drift, specified in degrees per hour

    Returns
    -------
    ndarray.float
        An array of data in degrees per hour, whose corresponding index are
        timestamps whose spacing is determined by the rate parameter.

    Raises
    ------

    ValueError
        If the seconds, minutes, and hours do not add up to a positive time.
    """

    time = (hours * 60 * 60
            + minutes * 60
            + seconds)

    if time <= 0:
        raise ValueError('Time must be greater than zero')

    a = np.zeros(1)

    return a
