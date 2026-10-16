import nidaqmx as ni
import numpy as np


def rec(fs, rec_time):
    with ni.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev2/ai0")
        task.timing.cfg_samp_clk_timing(fs, samps_per_chan=int(fs * rec_time))
        data = task.read(number_of_samples_per_channel=int(fs * rec_time))
    time = np.arange(len(data)) / fs
    return time, data


if __name__ == "__main__":
    fs = 44100
    rec_time = 1

    time, data = rec(fs, rec_time)
    data_zero_mean = data - np.mean(data)
    # 実効値の計算
    rms_value = np.sqrt(np.mean(data_zero_mean**2))

    print(f"ピーク値 {np.array(data).max()}V")
    print(f"実効値（こちらを使用）: {rms_value}V")
    np.savetxt(
        "94dB_reference.csv",
        np.column_stack((time, data)),
        delimiter=",",
        header="Time, Voltage",
        comments="",
    )
