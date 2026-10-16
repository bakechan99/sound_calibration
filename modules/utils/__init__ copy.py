import numpy as _np


def generate_time_array(
    fs: float,
    duration: float,
):
    n_samples = round(fs * duration)
    t = _np.linspace(0, duration, n_samples, endpoint=False)
    return t


def volt_to_dB(rec_volt: float, basevolt: float):
    dBSPL = 94 + 20 * _np.log10(rec_volt / basevolt)
    return dBSPL
