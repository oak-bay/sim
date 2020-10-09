import sys
import random
from enum import Enum
from sim import Environment


class EventScheduler:
    """ 事件调度器. """

    class TimerType(Enum):
        UNKNOWN = 0
        FIX = 1
        TIMES = 2
        RAND = 3

    def __init__(self, evt=None, **kwargs):
        """ 初始化.
        """
        self.evt = evt
        self.type = EventScheduler.TimerType.UNKNOWN
        self.dt = None
        self.rng = None
        self.times = None
        self._check_pt = None
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
        now, _ = env.time_info
        if self._check_and_update(now, env):
            if self.evt:
                self.evt(env)

    def __rand_time(self):
        return random.random() * (self.rng[1] - self.rng[0]) + self.rng[0]

    def _check_and_update(self, now, env) -> bool:
        if self.type == EventScheduler.TimerType.FIX:
            if self._check_pt is None:
                self._check_pt = env.clock_info[0]
            if self._check_pt is not None and now >= self._check_pt:
                self._check_pt += self.dt
                return True
        if self.type == EventScheduler.TimerType.RAND:
            if self._check_pt is None:
                self._check_pt = env.clock_info[0] + self.__rand_time()
            if self._check_pt is not None and now >= self._check_pt:
                self._check_pt += self.__rand_time()
                return True
        if self.type == EventScheduler.TimerType.TIMES:
            if self._check_pt is None and len(self.times) > 0:
                self._check_pt = self.times[0]
            if self._check_pt is not None and now >= self._check_pt:
                idx = self.times.index(self._check_pt) + 1
                self._check_pt = self.times[idx] if idx < len(self.times) else None
                return True
        return False
