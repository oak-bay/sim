import math
from collections import namedtuple
from typing import Tuple
from functools import partial
import numpy as np
from .. import Entity, vec, move
from .misc import Servo, Fov


class Radar(Entity):
    """ 雷达.

    Attributes:
         position: 位置.
         results: 所有结果.
         current_results: 最新结果.
    """

    def __init__(self, **kwargs):
        """ 初始化.

        :param pos: 雷达位置.
        :param out: 输出结果.
        :param a_range: 方位范围.
        :param e_range: 俯仰范围.
        :param r_range: 距离范围.
        :param rate: 刷新时间间隔 (s).
        :param remove: 消批时间 (s).
        """
        super().__init__(**kwargs)
        self.position = vec.vec([0, 0])  # 位置.
        self.sensor = Sensor(self, **kwargs)  # 传感器.
        self.result = ResultManager(**kwargs)
        self.set_params(**kwargs)

    def set_params(self, **kwargs):
        if 'pos' in kwargs:
            self.position = vec.vec(kwargs['pos'])

    def step(self, time_info):
        pass

    def access(self, others):
        t, _ = self.env.time_info
        temp_results = {}
        for other in others:
            if other.is_alive():
                ret = self.sensor.detect(other)
                if ret is not None:
                    temp_results[other.id] = ret
        self.result.accept(temp_results, t)

    def reset(self):
        self.result.reset()

    @property
    def results(self):
        """ 当前有效结果（包含部分为了维持批号的结果）"""
        return self.result.results()

    @property
    def current_results(self):
        """ 最新结果. """
        t, _ = self.env.time_info
        return self.result.current_results(t)


""" 雷达结果条目.
bid: 批号
time: 获取时间.
count: 当前批号下点数.
value: 探测结果值.
"""
RadarResult = namedtuple('RadarResult', ['bid', 'time', 'count', 'value'])


class ResultManager:
    """ 结果管理器. """

    def __init__(self, **kwargs):
        self._results = {}  # 全部结果.
        self._batch_id = 0  # 结果批号.
        self._time_recv = 1.0  # 数据接收间隔
        self._time_del = 6.0  # 数据删除间隔.
        self.set_params(**kwargs)

    def set_params(self, **kwargs):
        if 'rate' in kwargs:
            self._time_recv = float(kwargs['rate'])
        if 'remove' in kwargs:
            self._time_del = float(kwargs['remove'])

    def reset(self):
        self._results.clear()
        self._batch_id = 0

    def results(self):
        return self._results

    def current_results(self, t):
        """ 最新结果. """
        ret = {}
        for k, v in self._results.items():
            _, tp, _, _ = v
            if tp == t:
                ret[k] = v
        return ret

    def accept(self, curr_results, t):
        """ 合并结果.  """
        # 合并和新增结果.
        for obj_id, ret in curr_results.items():
            if obj_id in self._results:
                bid, tp, count, _ = self._results[obj_id]
                if t - tp >= self._time_recv:
                    self._results[obj_id] = RadarResult(bid, t, count + 1, ret)
            else:
                self._batch_id += 1
                self._results[obj_id] = RadarResult(self._batch_id, t, 1, ret)

        # 删除过期结果.
        del_ids = []
        for obj_id, ret in self._results.items():
            _, tp, _, _ = self._results[obj_id]
            if t - tp >= self._time_del:
                del_ids.append(obj_id)
        for eid in del_ids:
            self._results.pop(eid)


class Sensor:
    """ 探测器. """

    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.fov = Fov(**kwargs)
        out = 'ar' if 'out' not in kwargs else kwargs['out']
        self.detect_policy = partial(detect_aer, out=out)

    def detect(self, other):
        """ 探测."""
        ret = self.fov.view(other.position, pos=self.position)
        if ret is not None:
            if self.detect_policy is not None:
                ret = self.detect_policy(self, other)
            return ret
        return None

    @property
    def position(self):
        return self.parent.position


def check_attribs(obj, attribs=None) -> bool:
    """ 检查对象是否包含属性. """
    if attribs:
        for attrib in attribs:
            if not hasattr(obj, attrib):
                return False
    return True


def detect_aer(sensor, target, out='aer', attribs=None):
    """ 获取对象观测值. """
    if check_attribs(target, attribs):
        aer = move.xyz_to_aer(target.position, sensor.position)
        a, e, r = aer[0], aer[1], aer[2]
        if out == 'a':
            return a
        elif out == 'r':
            return r
        elif out == 'ae':
            return a, e
        elif out == 'ar':
            return a, r
        else:
            return a, e, r
    return None
