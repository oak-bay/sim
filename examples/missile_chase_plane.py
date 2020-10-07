"""
导弹追逐飞机.
"""

from sim import Environment
from sim.vec import dist, unit
from sim.move import MoveEntity, MovePolicy
from sim.recorder import PropRecorder
from sim.plot import plot_xy_dict


class TrackPolicy(MovePolicy):
    """ 跟踪策略. """
    def __init__(self, target=None):
        super().__init__()
        self.target = target

    def access(self, others):
        assert self.parent
        for obj in others:
            if self.target == obj.id:
                speed = dist(self.parent.vel)
                self.parent.vel = unit(obj.pos - self.parent.pos) * speed
                break


if __name__ == '__main__':
    env = Environment()

    recorder = PropRecorder(prop_name='pos', show=True)
    env.step_events.append(recorder)

    plane = env.add(MoveEntity(pos=[0, 0], vel=[1, 0]))
    missile = env.add(MoveEntity(pos=[0, -10], vel=[0, 2], policy=TrackPolicy(target=plane.id)))

    env.run()

    plot_xy_dict(recorder.records, '*')
