import math
from collections import namedtuple
from typing import Tuple
from functools import partial
import numpy as np
from .. import Entity, vec, move

RadarResult = namedtuple('RadarResult', ['bid', 'time', 'count', 'value'])


class Radar(Entity):
    """ 雷达. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.position = vec.vec([0, 0])  # 位置.
        self.sensor = Sensor(self)  # 传感器.
        self.servo = None  # 伺服.
        self.result = ResultManager()
        self.set_params(**kwargs)

    def set_params(self, **kwargs):
        if 'pos' in kwargs:
            self.position = vec.vec(kwargs['pos'])

    def step(self, time_info):
        if self.servo:
            self.servo.step(time_info)

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

    @property
    def direction(self):
        """ 指向. """
        return (0.0, 0.0) if self.servo is None else self.servo.direction


class ResultManager:
    """ 结果管理器. """

    def __init__(self):
        self._results = {}  # 全部结果.
        self._batch_id = 0  # 结果批号.
        self._time_recv = 1.0  # 数据接收间隔
        self._time_del = 6.0  # 数据删除间隔.

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

    def __init__(self, parent):
        self.parent = parent
        self.fov = Fov()
        self.detect_policy = partial(detect_aer, out='ar')

    def detect(self, other):
        """ 探测."""
        ret = self.fov.view(other.position, pos=self.position, dir_=self.direction)
        if ret is not None:
            if self.detect_policy is not None:
                ret = self.detect_policy(self, other)
            return ret
        return None

    @property
    def direction(self):
        return self.parent.direction

    @property
    def position(self):
        return self.parent.position


class Fov:
    """ 视场（Field of View）. """

    def __init__(self):
        self.a_range = None
        self.e_range = None
        self.r_range = None

    def view(self, target, pos, dir_=None):
        """ 观察目标，是否能看到目标.

        :param target: 观察目标.
        :param pos: 观察地点.
        :param dir_: 观察轴线方向.
        :return: 如果看不到目标，返回None. 返回目标在视场里的方位 (AER).
        """
        aer = move.xyz_to_aer_ex(target, pos, dir_=dir_)
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
        aer = move.xyz_to_aer_ex(target.position, sensor.position, sensor.direction)
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
