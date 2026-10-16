import numpy as _np
import scipy.signal as signal

from . import _soundbase, _taper


# TODO: classにする
def generate_nbn(
    freq: int,
    band_width: int,
    amplitude: float,
    duration: float,
    taper_dur: float,
    fs: float,
    filter_order: int,
):
    # ホワイトノイズを生成
    noise = _soundbase.generate_whitenoise_base(duration, fs)

    # バンドパスフィルタ
    nyquist = fs / 2
    low = (freq - band_width / 2) / nyquist
    high = (freq + band_width / 2) / nyquist
    b, a = signal.butter(filter_order, [low, high], "band")

    # ノイズにフィルタをかける
    filtered_noise = signal.lfilter(b, a, noise)

    # 出力音の最大値を1に正規化
    out_sound = filtered_noise / _np.max(_np.abs(filtered_noise))

    # 振幅を適用
    out_sound *= amplitude

    # テーパーを適用
    out_sound = _taper.apply_taper(out_sound, taper_dur, fs)

    return out_sound
