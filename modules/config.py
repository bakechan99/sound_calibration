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
    duration: float
    volt_range: VoltRangeConfig

    # nbn 専用
    taper: float
    band_width: int
    freqs: list[int]
    filter_order: int = 4


class BbnConfig(_BaseModel):
    type: _Literal["bbn"]
    duration: float
    volt_range: VoltRangeConfig

    # bbn 専用
    taper: float = 0.01
    low_freq: float = 2000
    high_freq: float = 64000
    filter_order: int = 4


SoundConfig = _Union[NbnConfig, BbnConfig]


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
