from .. import Entity, vec
from enum import Enum


class JamType(Enum):
    """ 干扰类型. """
    DATALINK = 0  # 数据链.
    GPS = 1   # GPS


class Jammer(Entity):
    """ 干扰机. 
    
    Attributes:
        position: 位置.
        switch_on: 开关.
        kind: 干扰类型. gps,
        freq: 载频（MHz）
        power: 功率 (dBW)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.position = None
        self.switch_on = False
        self.kind = JamType.DATALINK
        self.freq = 2.4e3
        self.power = 0.0
        self.set_params(**kwargs)

    def set_params(self, **kwargs):
        if 'kind' in kwargs:
            self.kind = kwargs['kind']
        if 'pos' in kwargs:
            self.position = vec.vec(kwargs['pos'])
        if 'freq' in kwargs:
            self.freq = float(kwargs['freq'])
        if 'power' in kwargs:
            self.freq = float(kwargs['power'])
