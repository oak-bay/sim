from sim import Entity
from .vec import vec


def move_to_rel(pos, target, d):
    """ 按照相对速度移动.

    :param pos:
    :param target:
    :param d:
    :return: (new_pos, d_left)
    """
    if vec.dist(pos, target) > 0.0:
        v = vec.unit(target - pos)
        return pos + d * v, d - vec.dist(v)
    else:
        return pos, d


class MoveEntity(Entity):
    """ 运动对象. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._copy_props += ['pos', 'vel']
        self.pos0, self.vel0 = 0, 0
        self.pos, self.vel = 0, 0
        self.policy = None
        self.set_params(**kwargs)

    def reset(self):
        self.pos = self.pos0
        self.vel = self.vel0

    def set_params(self, **kwargs):
        if 'pos' in kwargs:
            self.pos0 = vec(kwargs['pos'])
        if 'vel' in kwargs:
            self.vel0 = vec(kwargs['vel'])
        if 'policy' in kwargs:
            self.policy = kwargs['policy']
            self.policy.parent = self

    def step(self, time_info):
        _, dt = time_info
        self.pos += dt * self.vel

    def access(self, others):
        if self.policy is not None:
            self.policy.access(others)


class MovePolicy:
    """ 运动策略. """

    def __init__(self):
        self.parent = None

    def access(self, others):
        pass
