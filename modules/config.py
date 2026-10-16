import os as _os
from typing import Literal as _Literal, Union as _Union

import numpy as _np
from pydantic import BaseModel as _BaseModel


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


class BbnConfig(_BaseModel):
    type: _Literal["bbn"]
    duration: float
    volt_range: VoltRangeConfig


SoundConfig = _Union[NbnConfig, BbnConfig]


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
