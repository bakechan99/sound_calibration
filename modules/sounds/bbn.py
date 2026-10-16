from . import _soundbase,_taper
import scipy.signal as signal
import numpy as _np


def generate_whitenoise(amplitude: float, duration: float, fs: float):
    # ホワイトノイズを生成
    noise = _soundbase.generate_whitenoise_base(duration, fs)

    #2k~64kHzの幅で作成
    nyquist = fs / 2
    low = 2000 / nyquist
    high = 64000 / nyquist
    b, a = signal.butter(4, [low, high], "band")

    # ノイズにフィルタをかける
    filtered_noise = signal.lfilter(b, a, noise)

    # 出力音の最大値を1に正規化
    out_sound = filtered_noise / _np.max(_np.abs(filtered_noise))

    # 振幅を適用
    out_sound *= amplitude

    # テーパーを適用
    out_sound = _taper.apply_taper(out_sound, 0.01, fs)


    # # 振幅を適用
    # noise *= amplitude

    # # テーパーを適用 
    # # out_sound = _taper.apply_taper(out_sound, taper_dur, fs)

    return out_sound
