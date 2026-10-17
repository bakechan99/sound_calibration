# =========================================import========================================
# データを扱うためのライブラリ
# DAQ を利用するためのライブラリ
import nidaqmx as ni  # nidaq 用
import numpy as np

# ========================ユーザーが操作する部分===========================
# 出力デバイス（Dev2 : M302 の青いDAQ）
output_device = "Dev2"
ao_ch = "ao0"  # 出力チャンネル

# 音波形関連
sound_sample_rate = 40000  # [Hz]
sound_duration = 0.0001  # [s]
sound_voltage = 2  # [V]
print(f"出力電圧：{sound_voltage}")


# =================================== デバイスコントロール関連 ======================================
# 音波形作成（クリック音のコード）
def make_sound_click(sound_sample_rate, stim_interval, sound_voltage):
    nsamples = int(sound_sample_rate * stim_interval)
    click = np.full(nsamples, sound_voltage)
    return click


# 音出力
def sound_output(
    outdata,
    sound_sample_rate,
    ao_ch,  # output 関連の変数
):
    trigger_nsamples = len(outdata)  # 出力予定のデータのデータ数を取得

    # タスクの設定
    with ni.Task(new_task_name="output") as write_task:
        # 入出力のチャンネルをマッピングする
        aochan = write_task.ao_channels.add_ao_voltage_chan(ao_ch)
        aochan.ao_max = 10  # output range of USB-4431
        aochan.ao_min = -10

        write_task.timing.cfg_samp_clk_timing(
            rate=sound_sample_rate,
            source="OnboardClock",
            samps_per_chan=trigger_nsamples,
        )

        # タスクのスタート
        write_task.start()


# ============================================================== 実行部分 ================================================================
if __name__ == "__main__":
    # 波形の構成
    sound = make_sound_click(sound_sample_rate, sound_duration, sound_voltage)

    # 出力
    sound_output(outdata=sound, sound_sample_rate=sound_sample_rate, ao_ch=ao_ch)

    # ログ
    print(f"OutputClick {sound_voltage}V {sound_duration * 1000}ms")
