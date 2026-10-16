import numpy as _np


def apply_taper(signal: _np.ndarray, rise_dur: float,fs: int):
    #テーパーを作成
    n_rise_samples = round(fs * rise_dur)
    taper = _np.linspace(0, 1, n_rise_samples)

    #信号をコピー
    new_signal = signal.copy()
    
    #テーパーを適用
    new_signal[:n_rise_samples] *= taper
    new_signal[-n_rise_samples:] *= taper[::-1]

    return new_signal