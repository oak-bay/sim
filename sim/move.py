from sim import Entity
from . import vec
import copy


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


class Track:
    """ 航线. """

    def __init__(self, **kwargs):
        self.waypoints = []
        self.wp_index = 1
        self.set_params(**kwargs)

    def set_params(self, **kwargs):
        if 'track' in kwargs:
            for wp in kwargs['track']:
                self.waypoints.append(vec.vec(wp))
        if 'back' in kwargs and len(self.waypoints) > 0:
            self.waypoints.append(self.waypoints[0])

    def current_wp(self):
        """ 获取当前目标航点. """
        if self.is_ok() and not self.is_over():
            return self.waypoints[self.wp_index]
        return None

    def next_wp(self):
        self.wp_index += 1

    def is_ok(self) -> bool:
        """ 航线是否可用. """
        return len(self.waypoints) >= 2

    def is_over(self) -> bool:
        """ 航线是否结束. """
        return self.wp_index >= len(self.waypoints)

    def start(self):
        """ 航线起始点. """
        return self.waypoints[0] if self.is_ok() else None


def move_to(pos, dest, dist):
    """ 向一个目标移动. """
    d = vec.dist(pos, dest)
    if d > dist:
        pos += vec.unit(dest - pos) * dist
    else:
        pos = copy.copy(dest)
    return pos, d - dist


def move_on_track(pos, track, dist):
    """ 沿航路移动一定距离. """
    left_dist = dist
    while left_dist > 0.0:
        wp = track.current_wp()
        if wp is None:
            break
        d = vec.dist(wp, pos)
        if d > left_dist:
            pos += vec.unit(wp - pos) * left_dist
            break
        else:
            pos = copy.copy(wp)
            left_dist -= d
            track.next_wp()
    return pos
