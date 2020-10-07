"""
多体运动.
"""

from sim import Environment
from sim.vec import vec, dist, unit
from sim.move import MoveEntity, MovePolicy
from sim.recorder import PropRecorder
from sim import plot

G = 1.0e3


class GravityPolicy(MovePolicy):
    """ 引力策略. """

    def access(self, others):
        assert self.parent
        f0 = vec([0, 0])
        _, dt = self.parent.env.time_info
        for obj in others:
            r = dist(self.parent.pos, obj.pos)
            f = unit(obj.pos - self.parent.pos) * G * obj.m / (r ** 2)
            f0 = f0 + f
        self.parent.vel += f0 * dt


if __name__ == '__main__':
    env = Environment()

    recorder = PropRecorder(prop_name='pos')
    env.step_events.append(recorder)

    earth = env.add(MoveEntity(props={'m': 2}, pos=[-100, 0], vel=[0, -1], policy=GravityPolicy()))
    moon = env.add(MoveEntity(props={'m': 1}, pos=[100, 0], vel=[0, 1], policy=GravityPolicy()))

    env.run(stop=2000.)

    plot.plot_xy_dict(recorder.records)
