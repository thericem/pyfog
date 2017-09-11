# coding: utf-8
"""Methods for simulating FOG performance in an aircraft with perfect
accelerometers.
"""

import numpy as np
from .experiment import Tombstone


def simulate_tombstone(
        rate=1,  # Hz
        seconds=0,
        minutes=0,
        hours=0,
        arw=0,
        drift=0,
        correlation_time=1800
        ):
    """Generates a stochastic error simulation based on performance indicators.
    Note that this method uses a definition of bias stability that takes the
    standard deviation of 10-second averages. The algorithm is taken from
    [#Lv]_.

    In order to recreate the same results that Lv et al show, enter the
    following command:

    >>> data = simulate_fog_single(rate=50, hours=4, arw=.0413,
    ...      drift=.944, correlation_time=3600)

    For more information on the algorithm, refer to [#Lv]_.


    .. [#Lv] Lv, P., Lai, J., Liu, J., & Qin, G. (2014). Stochastic error
       simulation method of fiber optic gyros based on performance indicators.
       Journal of the Franklin Institute, 351(3), 1501–1516.
       http://doi.org/10.1016/j.jfranklin.2013.11.007

    .. note:: Atleast one of `seconds`, `minutes`, or `hours` must be positive,
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

    # Set the parameters used by Lv et al
    Ta = 10  # 10 seconds
    ΔT = 1/rate  # sampling time, user-defined
    qx = drift  # bias drift, user-defined
    Tm = correlation_time  # bias drift, user-defined, default 1800 s
    T = time  # total time, user-defined

    # Equation 5 in Lv
    qw = arw * 60 / np.sqrt(ΔT)

    if drift:
        # Equation 20 in Lv
        qmw = np.sqrt(
            (qx**2 - qw**2/(Ta/ΔT))
            * np.pi/2 * (1-np.exp(-2*ΔT/Tm))
            / (np.arctan(np.pi*Tm/Ta) - np.arctan(np.pi*Tm/T))
        )
    else:
        qmw = 0

    # Equation 3 in Lv
    markov = np.zeros(arr_size)
    for i in range(1, arr_size):
        markov[i] = (np.exp(-ΔT/Tm) * markov[i-1]
                     + np.random.randn() * qmw)

    noise = np.random.randn(arr_size) * qw

    # Equation 2 in Lv
    data = noise + markov 
    return Tombstone(data=data, rate=rate) 


def get_cross_track_error(data, rate, velocity):
    """Returns the final cross-track position (in nautical miles)

    The algorithm simulates an aircraft traveling on a straight trajectory who
    turns according to the data provided. The aircraft instantaneously updates
    its heading at each timestep by Ω * Δt.

    .. warning: This code assumes that the magnitude of the rotations in data
       is small in order to use a paraxial approximation sin(\theta) = \theta.
       This paraxial approximation speeds up the algorithm, which is important
       if cross track error simulations will occur hundreds of times.

    This can be used in conjunction with `simulate_fog_single`. In order to
    simulate a transpacific flight and estimate the cross-track error for a
    single run, one could run:

    >>> rate = 1 # Hz
    >>> data = simulate_fog_single(rate=rate, hours=10, arw=.0413,
    ...      drift=.944, correlation_time=3600)
    >>> xtk = get_cross_track_error(data, rate, 900)

    Parameters
    ----------
    data: ndarray.float
        An array of rotation rates, in deg/h
    rate: float
        The sampling rate of data in Hz
    velocity: float
        The velocity of the simulated aircraft in kph

    Returns
    -------
    float
        The cross track error from this FOG signal.
    """

    Δθ = data * np.pi/180/3600/rate  # radians

    heading = np.cumsum(Δθ)

    Δy = velocity * 1000 / 3600 / rate * heading  # m
    xtk = np.cumsum(Δy) / 1852  # nmi

    return xtk
