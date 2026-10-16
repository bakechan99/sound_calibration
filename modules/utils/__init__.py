import numpy as _np


def generate_time_array(
    fs: float,
    duration: float,
):
    n_samples = round(fs * duration)
    t = _np.linspace(0, duration, n_samples, endpoint=False)
    return t


def peak_volt(signal):
    # DC成分を除いた信号の絶対値の最大（ピーク値）
    signal = _np.asarray(signal)
    return _np.max(_np.abs(signal - _np.mean(signal)))


def volt_to_dB(rec_volt: float, basevolt: float):
    dBSPL = 94 + 20 * _np.log10(rec_volt / basevolt)
    return dBSPL
