# coding: utf-8
"""This package provides support for Allan deviation and other algorithms.
"""

import numpy as np
from allantools import oadev


def allan_deviation(data, rate):
    """Returns the Allan deviation. Makes use of `oadev` from the `allantools` 
    repository

    Parameters
    ----------

    data: array_like(float)
        The data to be processed

    rate: float
        The sampling rate in Hz

    Returns
    -------

    tau: list of float
        The taus used in the Allan deviation
    dev: list of float
        The  Allan deviations.

    Examples
    --------

        >>>foo()
    """

    tau, dev, dev_error, N = oadev(data, rate=rate, data_type='freq')

    return tau, dev


def sigma_deviation(data, rate):
    """Returns the sigma deviation. For more details, consult [#Matthews]_.

    .. [#Matthews] Matthews, J.B., M.I. Gneses, D.S. Berg, "A high-resolution
       laser gyro,"
       Proc. IEEE NAECON, pp. 556-568, May 1978

    Parameters
    ----------

    data: array_like(float)
        The data to be processed

    rate: float
        The sampling rate in Hz

    Returns
    -------

    tau: list of float
        The taus used in the Allan deviation
    dev: list of float
        The  Allan deviations.
    """

    τs = np.unique((np.logspace(0, np.log10(len(data)), 30).astype(int)))
    σs = []

    for τ in τs:
        data_copy = data

        spacing = rate*τ
        leftovers = len(data_copy) % spacing
        if leftovers:
            data_copy = data_copy[:-leftovers]

        reshaped = np.mean(data_copy.reshape(-1, spacing), axis=1)
        sigma = np.std(reshaped)
        σs.append(sigma)

    return τs, σs
