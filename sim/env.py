import copy

from typing import Optional, Tuple, List
from .entity import Entity


class _SimClock:
    """ 仿真时钟."""

    def __init__(self):
        self._start = 0.
        self._stop = 10.
        self._step = 0.1
        self._now = self._start
        self._realtime = False

    def set_params(self, **kwargs):
        if 'start' in kwargs:
            self._start = float(kwargs['start'])
        if 'stop' in kwargs and float(kwargs['stop']) > self._start:
            self._stop = float(kwargs['stop'])
        if 'step' in kwargs and float(kwargs['step'] > 0):
            self._step = float(kwargs['step'])
        if 'realtime' in kwargs:
            self._realtime = bool(kwargs['realtime'])
        self.reset()

    def time_info(self) -> Tuple[float, float]:
        """ 当前时钟信息 (now, step)."""
        return self._now, self._step

    def info(self) -> Tuple[float, float, float]:
        """ 当前时钟信息 (now, step)."""
        return self._start, self._stop, self._step

    def reset(self):
        self._now = self._start

    def is_over(self) -> bool:
        return self._now > self._stop

    def step(self):
        self._now += self._step


class Environment:
    """ 环境.

    Properties:
        step_events: 场景步进事件列表.
            调用方式 event_handler(env)
    """

    def __init__(self):
        self._children = []  # List[Entity]
        self._clock = _SimClock()
        self.step_events = []

    def set_params(self, **kwargs):
        self._clock.set_params(**kwargs)

    @property
    def children(self):
        return self._children

    @property
    def clock_info(self) -> Tuple[float, float, float]:
        return self._clock.info()

    @property
    def time_info(self) -> Tuple[float, float]:
        """ 仿真场景时间信息 (now, step). """
        return self._clock.time_info()

    def add(self, obj: Entity) -> Optional[Entity]:
        """ 增加实体. """
        if obj and isinstance(obj, Entity):
            if not self.find(obj):
                self._children.append(obj)
                obj.env = self
            return obj
        return None

    def remove(self, tag):
        """ 移除实体. """
        if obj := self.find(tag):
            obj.env = None
            self._children.remove(obj)

    def find(self, tag) -> Optional[Entity]:
        """ 查找实体.

        :param tag: 对象标识. 可以是 Entity， id， name.
        :return: 返回环境中找到的对象.
        """
        for obj in self._children:
            if isinstance(tag, Entity) and tag is obj:
                return obj
            if isinstance(tag, int) and tag == obj.id:
                return obj
            if isinstance(tag, str) and tag == obj.name and tag != '':
                return obj
        return None

    def run(self, **kwargs):
        """ 运行. """
        self.set_params(**kwargs)
        self.reset()
        while not self.is_over():
            self.step()

    def step(self):
        """ 步进. """
        assert not self.is_over()

        # 相互交互.
        children = [obj for obj in self.children if obj.is_alive()]
        children_copy = copy.deepcopy(children)
        for obj in children:
            others = [e for e in children_copy if e.id != obj.id]
            obj.access(others)

        # 实体步进
        children = [obj for obj in self.children if obj.is_alive()]
        for obj in children:
            obj.step(self.time_info)

        # 处理事件.
        for evt in self.step_events:
            evt(self)

        # 时钟步进.
        self._clock.step()

    def is_over(self) -> bool:
        """ 判断是否结束. """
        return self._clock.is_over()

    def reset(self):
        self._clock.reset()
        for obj in self._children:
            obj.reset()
