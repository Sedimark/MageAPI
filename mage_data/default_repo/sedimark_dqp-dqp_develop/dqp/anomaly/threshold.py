##Copyright 2023 NUID UCD. All Rights Reserved.


from pythresh.thresholds.aucp import AUCP

from pythresh.thresholds.iqr import IQR
from pythresh.thresholds.mad import MAD
from pythresh.thresholds.fwfm import FWFM
from pythresh.thresholds.yj import YJ
from pythresh.thresholds.zscore import ZSCORE
from pythresh.thresholds.qmcd import QMCD
from pythresh.thresholds.fgd import FGD
from pythresh.thresholds.dsn import DSN
from pythresh.thresholds.clf import CLF
from pythresh.thresholds.filter import FILTER
from pythresh.thresholds.wind import WIND
from pythresh.thresholds.eb import EB
from pythresh.thresholds.regr import REGR
from pythresh.thresholds.boot import BOOT
from pythresh.thresholds.mcst import MCST
from pythresh.thresholds.hist import HIST
from pythresh.thresholds.moll import MOLL
from pythresh.thresholds.chau import CHAU
from pythresh.thresholds.gesd import GESD
from pythresh.thresholds.mtt import MTT
from pythresh.thresholds.ocsvm import OCSVM
from pythresh.thresholds.decomp import DECOMP
from pythresh.thresholds.meta import META
from pythresh.thresholds.vae import VAE
from pythresh.thresholds.gamgmm import GAMGMM
import numpy as np


class SimpleContamination():
    
    _is_fit = False
    
    def __init__(self, contamination=0.05, **params):
        
        self.contamination = contamination
        assert contamination < 1.0
       
    
    def fit(self, scores):
    
        sorted_scores = np.sort(scores)
        self.thresh_ = sorted_scores[ -int(len(sorted_scores) * self.contamination)]
        self._is_fit =  True
        
    def eval(self, scores):

        return scores >= self.thresh_


_AVAILABLE_THRESHOLDS = {
    
    'AUCP':AUCP,
    'contamination':SimpleContamination,
    'IQR':IQR,
    'MAD':MAD,
    'FWFM':FWFM,
    'YJ': YJ,
    'ZSCORE': ZSCORE,
    'QMCD': QMCD,
    'FGD': FGD,
    'DSN': DSN,
    'CLF': CLF,
    'FILTER': FILTER,
    'WIND': WIND,
    'EB': EB,
    'REGR': REGR,
    'BOOT': BOOT,
    'MCST': MCST,
    'HIST': HIST,
    'MOLL': MOLL,
    "CHAU": CHAU,
    'GESD': GESD,
    'MTT': MTT,
 #   'KARCH': KARCH,
    'OCSVM': OCSVM,
 #   'CLUST': CLUST,
    'DECOMP': DECOMP,
    'META': META,
    'VAE': VAE,
 #   'CPD': CPD,
    'GAMGMM': GAMGMM,
}

class Threshold():
    
    def __init__ (self, threshold_type='contamination', **params):
        
        assert threshold_type  in _AVAILABLE_THRESHOLDS
        self._name = threshold_type
        self.thresh = _AVAILABLE_THRESHOLDS[threshold_type](**params)
        
    def eval(self, scores):
        
        if hasattr(self.thresh, 'fit') and not self.thresh._is_fit:
            
            self.thresh.fit( scores)
        return self.thresh.eval(scores)
    
    def __call__(self, scores):
        
        return self.eval(scores)

    def _list_threshold_models():
        return list(_AVAILABLE_THRESHOLDS.keys())
       
        
        
