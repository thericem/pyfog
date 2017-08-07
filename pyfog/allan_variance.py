from math import log, floor, sqrt, ceil
from scipy.signal import lfilter, filtfilt
import numpy as np
import matplotlib.pyplot as plt




# Rotate at a known speed in one direction,
# and at a known speed in the opposite direction

def get_scale_factor(instruments,_dither_angle=5, _dither_velocity=1,
                     _padding=1,
                     ):
    import time
    # Guess at the variables
    rot = instruments['rotation_platform']
    lia = instruments['lock_in_amplifier']
    daq = instruments['data_acquisition_unit']

    """Return scale factor in terms of volts per (degree per hour)"""
    rot.velocity = _dither_velocity

    read_time = _dither_angle / _dither_velocity - _padding

    # Clear out a funky buffer...
    for i in range(5):
        freq = 1 / lia.time_constant

    rot.cw(.5*_dither_angle, background=True)
    time.sleep(.5)
    #lia.autogain()
    lia.sensitivity = 0.1
    while not rot.is_stationary():
        pass

    rot.ccw(.5*_dither_angle, background=True)
    time.sleep(0.5)
    lia.autophase()
    while not rot.is_stationary():
        pass

    rot.cw(_dither_angle, background=True)
    while True:
        if rot.is_constant_speed(): break
    cw_data = daq.read(seconds=read_time, frequency=freq,
                       max_voltage=lia.sensitivity)

    while not rot.is_stationary():
        pass

    rot.ccw(_dither_angle, background=True)
    while True:
        if rot.is_constant_speed(): break
    ccw_data = daq.read(seconds=_dither_angle / _dither_velocity - _padding,
                        frequency=freq, max_voltage=lia.sensitivity)

    while not rot.is_stationary():
        pass

    #rot.angle = 0

    # volts per degree per second
    vpdps = (abs(np.mean(cw_data)) + abs(np.mean(cw_data))) / (2 *
                                                            _dither_velocity)
    # compensate for stage pitch
    vpdps /= np.cos(37.4/180*np.pi)

    # degree per hour per volt
    dphpv = 1 / vpdps * 60 ** 2
    return dphpv

def allan_var(x, dt):
    """Computes the allan variance of signal x acquired with sampling rate 1/dt where dt is in seconds

    Paramters
    ---------
    x : array
        The data
    dt : float
        sampling rate 1/dt in seconds

    Returns
    -------
    tau : array
        Vector containing allan variance averaging times in units of [s]
    sig : array
        Vector containing allan deviations in units of [x] corresponding to averaging times in tau
    """

    # Get number of samples
    n = len(x)

    # set increment in tau to dB
    dTau = 3
    dTau = 10 ** (dTau / 10)
    dTau = 1.1  # 2

    # set the maximum value of tau to be 1/9 of the total number of samples
    # as per the IEEE FOG test document
    tauMax = n / 9

    # define tau to be an integer number of timesteps with logarithmic spacing
    # dTauIncrements
    #
    # (unique required because tau tends to be of form [1 1 2 ....])
    #tau = np.unique(
    #    dTau ** np.arange(
    #        ceil(log(len(x) / 9) / log(dTau))
    #    )
    #)

    tau = np.unique(
        np.ceil(dTau ** np.arange(
            np.ceil(log(len(x) / 9) / log(dTau))
        ))
    )

    sig = np.zeros_like(tau, dtype=float)

    for j in range(len(tau)):
        # define number of samples to average
        m = int(tau[j])

        # compute the running average of x with a window size m
        b = np.ones(m) / m
        y = lfilter(b, 1, x)

        # construct the delY(k) = y(k) - y(k-m)
        bp = np.zeros(m + 1)
        bp[0] = 1
        bp[-1] = -1
        delY = lfilter(bp, 1, y[m:-1])

        # the allan variance sig**2 is 1/2 the average value of delY**2
        # sig[j] = sqrt(0.5 * mean(delY[m+1:m:end])**2)

        # use this to compute maximally overlapping allan variance
        sig[j] = sqrt(0.5 * np.mean(delY[m + 1:-1] ** 2))

    return tau * dt, sig

def save_to_h5(filename, prefix, results_dict,instruments,overwrite=False):
    import h5py
    awg = instruments['function_generator']
    with  h5py.File(filename) as hdf5_file:
        try:
            hdf5_file.create_dataset(prefix + '/tau', data=results_dict['taus'])
            hdf5_file.create_dataset(prefix + '/sigma', data=results_dict['sigmas'])
        except Exception as err:
            if not overwrite:
                print(err)
                return
            if overwrite:
                print("Overwriting...\r")
                hdf5_file[prefix + '/tau'][...] = results_dict['taus']
                hdf5_file[prefix + '/sigma'][...] = results_dict['sigmas']
        hdf5_file[prefix].attrs['start_time'] = results_dict['start_time']
        hdf5_file[prefix].attrs['modulation_frequency'] = awg.freq
        hdf5_file[prefix].attrs['modulation_voltage'] = awg.voltage
        hdf5_file[prefix].attrs['modulation_waveform'] = awg.waveform
        hdf5_file[prefix].attrs['duration'] = results_dict['duration']
        hdf5_file[prefix].attrs['scale_factor'] = results_dict['scale_factor']
        hdf5_file[prefix].attrs['sensitivity'] = results_dict['sensitivity']
        hdf5_file[prefix].attrs['time_constant'] = results_dict['time_constant']
        hdf5_file[prefix].attrs['source_temperature'] = 20
        hdf5_file[prefix].attrs['source_current'] = 162.63


def acquire_allan_variance(instruments,h5_file_name=None,h5_prefix=None,
        seconds=0,minutes=0,hours=0,show_plot=False):
    rot = instruments['rotation_platform']
    lia = instruments['lock_in_amplifier']
    daq = instruments['data_acquisition_unit']
    awg = instruments['function_generator']

    duration = seconds + 60*minutes + 3600*hours
    if duration <= 0:
        raise Exception('Duration needs to be positive. Did you forget to '
                        'specify `seconds`, `minutes`, `hours`?')

    import time
    import threading
    from ipywidgets import FloatProgress, Label
    from IPython.display import display

    def update_progress(update_interval, progress_bar):
        time_passed = time.time() - start_time
        if time_passed < duration:
            # schedule another event
            threading.Timer(update_interval, update_progress,
                            [update_interval, progress_bar]).start()
            progress_bar.value = time_passed
        else:
            progress_bar.value = duration
            is_progress_updating = False
        m, s = divmod(int(progress_bar.value), 60)
        h, m = divmod(m, 60)
        l.value = "%d:%02d:%02d/%s" % (h, m, s, formatted_duration)

    l = Label()

    display(l)

    l.value = 'Calibrating and acquiring scale factor...'
    scale_factor = get_scale_factor(instruments)
    l.value = 'Setting sensitivity'
    lia.sensitivity = 0.001
    #lia.autogain()
    for i in range(5, 0, -1):
        l.value = 'Beginning acquisition in %i seconds...' % i
        time.sleep(1)

    start_time = time.time()
    end_time = start_time + duration

    m, s = divmod(duration, 60)
    h, m = divmod(m, 60)
    formatted_duration = "%d:%02d:%02d" % (h, m, s)

    progress_bar = FloatProgress(max=duration)

    display(progress_bar)
    update_progress(duration / 100, progress_bar)

    global voltage
    for i in range(5):
        tc = lia.time_constant
    voltage = daq.read(seconds=duration, frequency=1 / tc,
                       max_voltage=lia.sensitivity)
    global rotation
    rotation = scale_factor * voltage

    rate = len(rotation) / (duration)
    tau, sig = allan_var(rotation, 1 / rate)

    if show_plot:
        plt.loglog(tau, sig)
        plt.grid(ls=':', which='both')
        plt.title('Allan Variance')
        plt.ylabel(r'$\sigma$ ($^\circ$/hr)')
        plt.xlabel(r'$\tau$ (s)')

    for i in range(5): # Mysterious buffer precautionary measure
        sensitivity = lia.sensitivity

    acquisition_dict = {
        "start_time" : start_time,
        "time_constant" : tc,
        "duration" : duration,
        "taus" : tau,
        "sigmas" : sig,
        "scale_factor" : scale_factor,
        "sensitivity" : lia.sensitivity,
        "raw_voltage" : voltage
    }

    if h5_file_name and h5_prefix:
        try:
            save_to_h5(h5_file_name, h5_prefix, acquisition_dict, instruments)
        except Exception as err:
            print(err)

    # Hide widgets
    l.close()
    progress_bar.close()

    return acquisition_dict