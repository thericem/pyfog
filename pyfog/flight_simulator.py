# coding: utf-8
"""Various code for running
some files
and line breaks
"""

import numpy as np


def generate_fog_single(
        rate=1,  # Hz
        seconds=0,
        minutes=0,
        hours=0,
        arw=0,
        drift=0,
        correlation_time=1800
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
    correlation_time: float, optional
        The correlation time in seconds. For more information, see "Stocastic
        error  simulation method of fiber optic gyros based on performance
        indicators" by Lv et al. They recommend a value between 1800 and 3600
        seconds.

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

    # Define the length in seconds
    time = (hours * 60 * 60
            + minutes * 60
            + seconds)
    if time <= 0:
        raise ValueError('Time must be greater than zero')

    arr_size = int(rate * time)

    correlation_time *= rate

    # Set the parameters used by Lv et al
    Ta = 10 * rate  # 10 seconds
    ΔT = 1/rate  # sampling time, user-defined
    qx = drift # bias drift, user-defined
    Tm = correlation_time #  bias drift, user-defined, default 1800 s
    qw = arw * 60 / np.sqrt(ΔT) # angular random walk, user-defined, equation 5 in Lv
    T = time # total time, user-defined

    # Equation 20 in Lv
    qmw = 0
#    qmw = np.sqrt((
#        qx**2 - qw**2/(Ta/ΔT)
#        )*(
#            np.pi/2 * (1-np.exp(-2*ΔT/Tm))
#            /
#            (np.arctan(np.pi*Tm/Ta) - np.arctan(np.pi*Tm/T))
#    ))

    markov = np.zeros(arr_size)
    for i in range(1, arr_size):
        markov[i] = (np.exp(-rate/correlation_time) * markov[i-1]
                     + np.random.randn() * qmw)

    noise = np.random.randn(arr_size) * qw

    return noise + markov
