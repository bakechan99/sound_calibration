import nidaqmx as _ni
import numpy as _np

def play_and_rec(
      out_sig: _np.ndarray,
      fs: float,
      device_str: str,
      ai_ch_str: str,
      ao_ch_str: str,

):
    ai_str = f"{device_str}/{ai_ch_str}"
    ao_str = f"{device_str}/{ao_ch_str}"

    n_samples = len(out_sig)
    duration = n_samples / fs

    with _ni.Task() as read_task, _ni.Task() as write_task:
        
        # AIチャンネルの作成
        read_task.ai_channels.add_ai_voltage_chan(ai_str)  

        read_task.timing.cfg_samp_clk_timing(fs, samps_per_chan=round(fs * duration))

        #TODO: なんかかぶってるからコメントアウト (いらなかったら消してください)
        # data = read_task.read(number_of_samples_per_channel = round(fs * duration))    

        # AOチャンネルの作成
        write_task.ao_channels.add_ao_voltage_chan(ao_str)
        write_task.timing.cfg_samp_clk_timing(fs, source="OnboardClock", samps_per_chan=n_samples)

        # 音を出力すると同時に計測を開始する「トリガー」の設定
        write_task.triggers.start_trigger.cfg_dig_edge_start_trig(read_task.triggers.start_trigger.term)

        #TODO auto_start=Trueにしたから動作をチェック
        write_task.write(out_sig, auto_start=True)

        data = read_task.read(number_of_samples_per_channel=round(fs * duration))
    
    data = _np.array(data).T

    return data