import numpy as _np


def generate_click(
    amplitude: float,
    width: float,
    onset: float,
    duration: float,
    fs: float,
    polarity: str,
):
    '''
    無音の中に矩形パルスを1発置いたクリック音を生成する
    前後は0Vなので出力終了後にDCが残らない
    '''
    n_samples = round(fs * duration)
    n_width = round(fs * width)
    n_onset = round(fs * onset)

    out_sound = _np.zeros(n_samples)

    # 矩形パルスを配置
    sign = 1 if polarity == "pos" else -1
    out_sound[n_onset : n_onset + n_width] = sign * amplitude

    return out_sound
