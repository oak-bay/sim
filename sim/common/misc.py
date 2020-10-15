"""
辅助类：
1. Antenna（天线）
2. Fov（视场）
3. Servo（伺服）
"""

from typing import Tuple, Optional
import numpy
from .. import move, vec


class Antenna:
    """ 天线. """
    pass


class Fov:
    """ 视场（Field of View）.

    Attributes:
        a_range: 方位角范围.
        e_range: 俯仰角范围.
        r_range: 距离范围.
    """

    def __init__(self, **kwargs):
        self.a_range = None
        self.e_range = None
        self.r_range = None
        self.set_params(**kwargs)

    def set_params(self, **kwargs):
        if 'a_range' in kwargs:
            self.a_range = kwargs['a_range']
        if 'e_range' in kwargs:
            self.e_range = kwargs['e_range']
        if 'r_range' in kwargs:
            self.r_range = kwargs['r_range']

    def view(self, target, pos, dir_=None) -> Optional[numpy.ndarray]:
        """ 观察目标，是否能看到目标.

        :param target: 观察目标.
        :param pos: 观察地点.
        :param dir_: 观察轴线方向.
        :return: 如果看不到目标，返回None. 返回目标在视场里的方位 (AER).
        """
        aer = move.xyz_to_aer(target, pos)
        if not self.in_range(aer):
            return None
        return aer

    def in_range(self, aer):
        a, e, r = aer[0], aer[1], aer[2]
        return move.in_range(r, self.r_range) and move.in_range(a, self.a_range, 'a') \
               and move.in_range(e, self.e_range, 'e')


class Servo:
    """ 伺服（用于控制设备指向）.  """

    def __init__(self):
        self._angle = [0.0, 0.0]  # 方位-俯仰指向（度）.
        self.speeds = [0.0, 0.0]
        self.az_limit = None
        self.el_limit = [0.0, 90.0]

    def step(self, time_info):
        pass

    @property
    def direction(self) -> Tuple[float, float]:
        """ 指向角度 (方位，俯仰) 度. """
        return tuple(self._angle)
