import json
import os

import nidaqmx as ni
import numpy as np

from modules.config import CalibConfig
from modules.utils import peak_volt


def rec(fs, rec_time, ai_str):
    with ni.Task() as task:
        task.ai_channels.add_ai_voltage_chan(ai_str)
        task.timing.cfg_samp_clk_timing(fs, samps_per_chan=int(fs * rec_time))
        data = task.read(number_of_samples_per_channel=int(fs * rec_time))
    time = np.arange(len(data)) / fs
    return time, data


if __name__ == "__main__":
    json_path = os.path.join("configs", "master.json")

    # jsonファイルの内容を取得
    with open(json_path, "r") as file:
        config_data = json.load(file)

    calib_config = CalibConfig(**config_data)
    daq = calib_config.daq
    ref = calib_config.reference

    time, data = rec(ref.fs, ref.duration, f"{daq.device}/{daq.ai_ch}")
    # ピーク値の計算（計測側と同じ定義）
    peak_value = peak_volt(data)

    print(f"ピーク値（baseline.volt に使用）: {peak_value}V")
    np.savetxt(
        ref.file,
        np.column_stack((time, data)),
        delimiter=",",
        header="Time, Voltage",
        comments="",
    )
