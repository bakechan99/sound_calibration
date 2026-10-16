import numpy as _np

def generate_whitenoise_base(
        duration: float,
        fs: float    
):
    '''
    振幅が1のホワイトノイズを生成する
    '''
    #サンプル数を計算
    n_samples = round(fs * duration)
    
    #ノイズを生成
    #TODO：　ランダムのシードになっているか調べる
    noise = _np.random.normal(0,1,n_samples)

    

    return noise