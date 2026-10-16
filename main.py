import json
import os

import modules
import modules.measure
import modules.measure.calibrate

if __name__ == "__main__":
    json_path = os.path.join("configs", "master.json")

    # jsonファイルの内容を取得
    with open(json_path, "r") as file:
        config_data = json.load(file)

    calib_config = modules.config.CalibConfig(**config_data)

    # calibrate() 内で全 sounds をループする
    modules.measure.calibrate.calibrate(calib_config)
