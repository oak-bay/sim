import sys
import random
from enum import Enum
from sim import Environment


class EventScheduler:
    """ 事件调度器.

    Usages:
        # env = Environment()
        # fun(env)
        env.step_events.append(EventScheduler(evt=fun, times=[1, 3])) # call at 1s, 3s
        env.step_events.append(EventScheduler(evt=fun, dt=0.2)) # call every 0.2s
        env.step_events.append(EventScheduler(evt=fun, rand=[1, 3])) # call at random interval between [1s, 3s]
    """

    class TimerType(Enum):
        UNKNOWN = 0
        FIX = 1
        TIMES = 2
        RAND = 3

    def __init__(self, evt=None, **kwargs):
        """ 初始化.

        :param evt: 事件处理函数.
        :param dt: 按照固定事件间隔调用事件.
        :param times: 按照规定的事件序列调用事件.
        :param rand: 按照随机的事件间隔调用事件.
        """
        self.evt = evt
        self.type = EventScheduler.TimerType.UNKNOWN
        self.dt = None
        self.rng = None
        self.times = None
        self._check_pt = None  # 当前检查时间点（用于启动事件）
        self._env = None
        self.set_params(**kwargs)

    def set_params(self, **kwargs):
        if 'dt' in kwargs:
            self.dt = float(kwargs['dt']) - 2 * sys.float_info.epsilon
            self.type = EventScheduler.TimerType.FIX
        if 'rand' in kwargs:
            self.rng = sorted(kwargs['rand'])
            self.type = EventScheduler.TimerType.RAND
        if 'times' in kwargs:
            self.times = sorted(list(set(kwargs['times'])))
            self.type = EventScheduler.TimerType.TIMES

    def __call__(self, env: Environment):
        self._env = env
        now, _ = env.time_info
        if self._check_and_update(now, env) and self.evt:
            self.evt(env)

    def __rand_time(self):
        return random.random() * (self.rng[1] - self.rng[0]) + self.rng[0]

    def _check_and_update(self, now, env) -> bool:
        if self.type == EventScheduler.TimerType.FIX:
            if self._check_pt is None:
                self._check_pt = env.clock_info[0]
            if self._check_now(now):
                self._check_pt += self.dt
                return True
        if self.type == EventScheduler.TimerType.RAND:
            if self._check_pt is None:
                self._check_pt = env.clock_info[0] + self.__rand_time()
            if self._check_now(now):
                self._check_pt += self.__rand_time()
                return True
        if self.type == EventScheduler.TimerType.TIMES:
            if self._check_pt is None and len(self.times) > 0:
                self._check_pt = self.times[0]
            if self._check_now(now):
                idx = self.times.index(self._check_pt) + 1
                self._check_pt = self.times[idx] if idx < len(self.times) else None
                return True
        return False

    def _check_now(self, now):
        assert self._env is not None
        if self._check_pt is not None:
            _, dt = self._env.time_info
            if dt > now - self._check_pt >= 0.0:
                return True
        return False

