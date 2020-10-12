import math
from functools import partial
from .. import Entity
from .. import vec

from collections import namedtuple
from typing import Tuple


RadarResult = namedtuple('RadarResult', ['bid', 'time', 'count', 'value'])


class Radar(Entity):
    """ 雷达. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.position = vec.vec([0, 0])
        self.sensor = Sensor(self)
        self.servo = None
        self._results = {}  # 全部结果.
        self._batch_id = 0  # 结果批号.
        self._time_recv = 1.0  # 数据接收间隔
        self._time_del = 6.0  # 数据删除间隔.
        self.set_params(**kwargs)

    def set_params(self, **kwargs):
        if 'pos' in kwargs:
            self.position = vec.vec(kwargs['pos'])

    def step(self, time_info):
        pass

    def access(self, others):
        temp_results = {}
        for other in others:
            if other.is_alive():
                ret = self.sensor.detect(other)
                if ret is not None:
                    temp_results[other.id] = ret
        self.merge_results(temp_results)

    def reset(self):
        self.results.clear()
        self._batch_id = 0

    @property
    def results(self):
        """ 当前有效结果（包含部分为了维持批号的结果）"""
        return self._results

    @property
    def current_results(self):
        """ 最新结果. """
        t, _ = self.env.time_info
        ret = {}
        for k, v in self._results.items():
            _, tp, _, _ = v
            if tp == t:
                ret[k] = v
        return ret

    @property
    def direction(self):
        """ 指向. """
        return (0.0, 0.0) if self.servo is None else self.servo.direction

    def merge_results(self, curr_results):
        """ 合并结果.  """
        # 合并和新增结果.
        t, _ = self.env.time_info
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

    def __init__(self, parent):
        self.parent = parent
        self.detect_policy = partial(detect_aer, aer='ar', attribs=['position'])

    def detect(self, other):
        """ 探测."""
        ret = self.detect_policy(other, self)
        return ret

    @property
    def position(self):
        return self.parent.position


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


def xyz_to_aer(pt1, pt0=None):
    """ AER (适应二坐标、三坐标)
    """
    pt = pt1 if pt0 is None else (pt1 - pt0)
    a = math.atan2(pt[1], pt[0])
    e = 0 if len(pt) == 2 else math.atan2(pt[2], vec.dist([pt[0], pt[1]]))
    r = vec.dist(pt)
    return math.degrees(a), math.degrees(e), r


def detect_aer(center, target, aer='aer', attribs=None):
    if attribs:
        for attrib in attribs:
            if not hasattr(target, attrib):
                return None
    a, e, r = xyz_to_aer(target.position, center.position)
    if aer == 'a':
        return a
    elif aer == 'r':
        return r
    elif aer == 'ae':
        return a, e
    elif aer == 'ar':
        return a, r
    else:
        return a, e, r
