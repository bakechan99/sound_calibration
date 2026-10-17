import time as _time

import numpy as _np
import pandas as _pd

from .. import config as _config
from .. import daq as _daq
from .. import sounds as _sounds
from .. import utils as _utils


def calibrate(calib_config: _config.CalibConfig):
    for sound in calib_config.sounds:
        if not sound.enabled:
            print(f"Skip {sound.type} (enabled: false)")
            continue

        if sound.type == "nbn":
            calib_func = calib_nbn
        elif sound.type == "bbn":
            calib_func = calib_bbn
        elif sound.type == "click":
            calib_func = calib_click
        else:
            print(f"Invalid sound type: {sound.type}")
            continue

        outdata = calib_func(sound, calib_config)

        # 印加電圧・取得電圧(ピーク値)・dBのデータを保存（生波形は保存しない）
        peak_save_path = calib_config.save.get_save_path(f"{sound.type}_peak.csv")
        calib_config.save.make_save_dir()
        outdata.to_csv(peak_save_path, index=False)


def _play_and_rec(out_sound, calib_config: _config.CalibConfig):
    daq = calib_config.daq
    return _daq.play_and_rec(
        out_sound, calib_config.fs, daq.device, daq.ai_ch, daq.ao_ch
    )


def calib_nbn(sound: _config.NbnConfig, calib_config: _config.CalibConfig):
    outdata = {
        "Freq": [],
        "Vout": [],
        "Vin": [],
        "dB": [],
    }
    for freq in sound.freqs:
        for volt in sound.volt_range.voltages:
            out_sound = _sounds.generate_nbn(
                freq,
                sound.band_width,
                volt,
                sound.duration,
                sound.taper,
                calib_config.fs,
                sound.filter_order,
            )

            rec_signal = _play_and_rec(out_sound, calib_config)

            # 録音した信号のピーク値を計算
            rec_volt = _utils.peak_volt(rec_signal)

            rec_dB = _utils.volt_to_dB(rec_volt, calib_config.baseline.volt)

            # データを格納
            outdata["Freq"].append(freq)
            outdata["Vout"].append(volt)
            outdata["Vin"].append(rec_volt)
            outdata["dB"].append(rec_dB)
            # 各音の再生後に1秒間の間隔を空ける
            _time.sleep(1)

    outdata = _pd.DataFrame(outdata)
    return outdata


def calib_bbn(sound: _config.BbnConfig, calib_config: _config.CalibConfig):
    outdata = {
        "Vout": [],
        "Vin": [],
        "dB": [],
    }
    for volt in sound.volt_range.voltages:
        out_sound = _sounds.generate_whitenoise(
            volt,
            sound.duration,
            calib_config.fs,
            sound.low_freq,
            sound.high_freq,
            sound.filter_order,
            sound.taper,
        )

        rec_signal = _play_and_rec(out_sound, calib_config)

        # 録音した信号のピーク値を計算
        rec_volt = _utils.peak_volt(rec_signal)

        rec_dB = _utils.volt_to_dB(rec_volt, calib_config.baseline.volt)

        # データを格納
        outdata["Vout"].append(volt)
        outdata["Vin"].append(rec_volt)
        outdata["dB"].append(rec_dB)
        # 各音の再生後に1秒間の間隔を空ける
        _time.sleep(1)

    outdata = _pd.DataFrame(outdata)
    return outdata


def calib_click(sound: _config.ClickConfig, calib_config: _config.CalibConfig):
    outdata = {
        "Vout": [],
        "Vin": [],
        "dB": [],
    }
    for volt in sound.volt_range.voltages:
        out_sound = _sounds.generate_click(
            volt,
            sound.width,
            sound.onset,
            sound.duration,
            calib_config.fs,
            sound.polarity,
        )

        rec_signal = _play_and_rec(out_sound, calib_config)

        # 録音した信号のピーク値を計算
        rec_volt = _utils.peak_volt(rec_signal)

        rec_dB = _utils.volt_to_dB(rec_volt, calib_config.baseline.volt)

        # データを格納
        outdata["Vout"].append(volt)
        outdata["Vin"].append(rec_volt)
        outdata["dB"].append(rec_dB)
        # 各音の再生後に1秒間の間隔を空ける
        _time.sleep(1)

    outdata = _pd.DataFrame(outdata)
    return outdata
