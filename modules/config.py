import os as _os
from typing import Literal as _Literal, Union as _Union

import numpy as _np
from pydantic import BaseModel as _BaseModel, model_validator as _model_validator


class VoltRangeConfig(_BaseModel):
    v_start: float
    v_end: float
    num_points: int

    @property
    def voltages(self):
        return _np.logspace(
            _np.log10(self.v_start), _np.log10(self.v_end), self.num_points
        )


class NbnConfig(_BaseModel):
    type: _Literal["nbn"]
    enabled: bool = True
    duration: float
    volt_range: VoltRangeConfig

    # nbn 専用
    taper: float
    band_width: int
    freqs: list[int]
    filter_order: int = 4


class BbnConfig(_BaseModel):
    type: _Literal["bbn"]
    enabled: bool = True
    duration: float
    volt_range: VoltRangeConfig

    # bbn 専用
    taper: float = 0.01
    low_freq: float = 2000
    high_freq: float = 64000
    filter_order: int = 4


class ClickConfig(_BaseModel):
    type: _Literal["click"]
    enabled: bool = True
    # 1音あたりのデータ取得区間（この中にクリックを1発置く）
    duration: float = 1.0
    volt_range: VoltRangeConfig

    # click 専用
    width: float = 0.0001  # パルス幅 [s]
    onset: float = 0.01  # 区間の先頭からクリックまでの無音 [s]
    polarity: _Literal["pos", "neg"] = "pos"


SoundConfig = _Union[NbnConfig, BbnConfig, ClickConfig]


class DaqConfig(_BaseModel):
    device: str = "Dev2"
    ai_ch: str = "ai0"
    ao_ch: str = "ao0"


class ReferenceConfig(_BaseModel):
    # sound_calibrator.py で94dB基準音を録音する設定
    fs: int = 44100
    duration: float = 1.0
    file: str = "94dB_reference.csv"


class BaselineConfig(_BaseModel):
    volt: float


class SaveConfig(_BaseModel):
    dirs: list[str]
    prefix: str
    suffix: str

    def make_save_dir(self):
        _os.makedirs(_os.path.join(*self.dirs),exist_ok=True)

    def get_save_path(self, file_name: str):
        # 新しいファイル名を作成
        fname, ext = _os.path.splitext(file_name)
        new_file_name = self.prefix + fname + self.suffix + ext
        # 保存先のパスを返す
        return _os.path.join(*self.dirs, new_file_name)


class CalibConfig(_BaseModel):
    save: SaveConfig
    fs: int
    baseline: BaselineConfig
    sounds: list[SoundConfig]
    daq: DaqConfig = DaqConfig()
    reference: ReferenceConfig = ReferenceConfig()

    @_model_validator(mode="after")
    def _check_filter_band(self):
        # フィルタの帯域が 0 < f < fs/2 に収まっているか確認
        nyquist = self.fs / 2
        for sound in self.sounds:
            # 計測しない音はチェックしない
            if not sound.enabled:
                continue
            if sound.type == "click":
                self._check_click(sound)
                continue
            if sound.type == "nbn":
                bands = [
                    (f - sound.band_width / 2, f + sound.band_width / 2)
                    for f in sound.freqs
                ]
            elif sound.type == "bbn":
                bands = [(sound.low_freq, sound.high_freq)]
            for low, high in bands:
                if not 0 < low < high < nyquist:
                    raise ValueError(
                        f"{sound.type}: band {low}-{high}Hz must satisfy "
                        f"0 < low < high < fs/2 ({nyquist}Hz)"
                    )
        return self

    def _check_click(self, sound: ClickConfig):
        # パルス幅がサンプル数の整数倍になっているか確認
        n_width = sound.width * self.fs
        if round(n_width) < 1 or abs(n_width - round(n_width)) > 1e-6:
            raise ValueError(
                f"click: width {sound.width}s is not an integer number of "
                f"samples at fs={self.fs}Hz ({n_width} samples)"
            )
        # クリックが区間内に収まり，最後が0Vで終わるか確認
        if not (0 < sound.onset and sound.onset + sound.width < sound.duration):
            raise ValueError(
                f"click: must satisfy 0 < onset and onset + width < duration "
                f"(onset={sound.onset}, width={sound.width}, duration={sound.duration})"
            )
