"""
雷达探测 UAV.
"""

import math
from sim import Environment, Entity
from sim.vec import vec, dist
from sim.recorder import EntityPropRecorder
from sim import plot


class Uav(Entity):
    """ UAV.
    无人机按预定航迹飞行.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pos = vec([100, 0])
        self.vel = vec([1, 1])

    def step(self, time_info):
        _, dt = time_info
        self.pos += dt * self.vel


class Radar(Entity):
    """ 雷达.

    探测飞行物体位置.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pos = vec([0, 0])
        self.result = None

    def access(self, others):
        self.result = None
        for other in others:
            if isinstance(other, Uav):
                v = other.pos - self.pos
                r = dist(v)
                a = math.atan2(v[1], v[0])
                self.result = [r, a]


if __name__ == '__main__':
    env = Environment()
    uav = env.add(Uav())
    radar = env.add(Radar())

    recorder = EntityPropRecorder(radar, 'result')
    env.step_events.append(recorder)

    env.run()

    plot.plot_xy(recorder.records)
