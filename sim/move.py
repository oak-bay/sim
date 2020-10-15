import copy
import math
import numpy as np
from sim import Entity
from . import vec


##############################################################################
# 坐标转换.
# XYZ 坐标系. X轴:正东；Y轴:正北；Z轴：向上;
# AER 坐标系.
#   A(方位):正北，顺时针,0~360°；
#   E(俯仰):向上,-90~90°；
#   R(距离):>=0
##############################################################################


def xyz_to_aer(xyz, origin=None, angle='d'):
    """ XYZ 转换至 AER 坐标.

    :param xyz: 坐标.
    :param origin: 坐标原点.
    :param angle: 角度结果输出方式. 'd' 角度输出； 'r' 弧度输出.
    :return: 转换后 AER 坐标.
    """
    assert vec.dim(xyz) == 3

    pt = xyz if origin is None else (xyz - origin)
    a = math.atan2(pt[0], pt[1])
    if a < 0:
        a += 2 * math.pi
    e = math.atan2(pt[2], vec.dist([pt[0], pt[1]]))
    r = vec.dist(pt)
    if angle == 'd':
        return math.degrees(a), math.degrees(e), r
    else:
        return a, e, r


def aer_to_xyz(aer, origin=None, angle='d'):
    """ AER 转换至 XYZ 坐标.

    :param aer: AER坐标.
    :param origin: 坐标原点.
    :param angle: 角度结果输出方式. 'd' 角度输出； 'r' 弧度输出.
    :return: 转换后 XYZ 坐标.
    """
    assert vec.dim(aer) == 3

    if angle == 'd':
        a, e, r = math.radians(aer[0]), math.radians(aer[1]), aer[2]
    else:
        a, e, r = aer[0], aer[1], aer[2]
    z = r * math.sin(e)
    y = r * math.cos(e) * math.cos(a)
    x = r * math.cos(e) * math.sin(a)
    pt = vec.vec([x, y, z])
    return pt if origin is None else (pt + origin)


def xyz_to_aer_ex(xyz, origin, dir_, angle='d'):
    """ XYZ 转换至 AER 坐标.

    :param xyz: 坐标.
    :param origin: 坐标原点.
    :param dir_: 坐标原点轴线方向.
    :param angle: 角度结果输出方式. 'd' 角度输出； 'r' 弧度输出.
    :return: 转换后 AER 坐标.
    """
    pt = (xyz - origin) if dir_ is None else vec.trans(xyz - origin, mat_ae(dir_))
    aer = xyz_to_aer(pt, angle=angle)
    return aer


##############################################################################
# 辅助矩阵.
##############################################################################


def mat_r3x(a):
    """ X 轴旋转3维矩阵.

    :param a: 旋转角度（弧度）.
    :return: 旋转矩阵.
    """
    return np.mat([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]], dtype=np.float)


def mat_r3y(a):
    """ Y 轴旋转3维矩阵.

    :param a: 旋转角度（弧度）.
    :return: 旋转矩阵.
    """
    return np.mat([[math.cos(a), 0, math.sin(a)], [0, 1, 0]], [-math.sin(a), 0, math.cos(a)], dtype=np.float)


def mat_r3z(a):
    """ Z 轴旋转3维矩阵.

    :param a: 旋转角度（弧度）.
    :return: 旋转矩阵.
    """
    return np.mat([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]], dtype=np.float)


def mat_ae(ae, type_='d'):
    """ 方位/俯仰旋转矩阵（3维）.

    TODO: IMPLEMENT
    """
    a, e = ae[0], ae[1]
    if type_ == 'd':
        a, e = math.radians(a), math.radians(e)

    ma = [[math.cos(a), math.sin(a), 0], [-math.sin(a), math.cos(a), 0], [0, 0, 1]]
    ma = np.array(ma, dtype=np.float).T

    mb = [[1, 0, 0], [0, math.cos(e), -math.sin(e)], [0, math.sin(e), math.cos(e)]]
    mb = np.array(mb, dtype=np.float).T

    return np.dot(mb, ma)


def mat_a(a, type_='d'):
    """ 方位旋转矩阵（2维, 顺时针为正.）.

    TODO: IMPLEMENT
    """
    if type_ == 'd':
        a = math.radians(a)
    m = [[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]]
    return np.array(m, dtype=np.float).T


##############################################################################
# 运动函数.
##############################################################################

def move_to(pos, dest, d):
    """ 向一个目标移动.

    :param pos: 当前位置.
    :param dest: 目标位置.
    :param d: 期望移动的距离.
    :return: (运动后位置, 剩余距离)
    """
    di = vec.dist(pos, dest)
    if di > d:
        pos = copy.copy(pos) + vec.unit(dest - pos) * d
    else:
        pos = copy.copy(dest)
    return pos, di - d


def in_range(val, rng, type_=''):
    """ 判断数值是否在规定范围内.

    Usages:
        in_range(1, [0, 2])  # True
        in_range(0, [270, 90])  # True

    :param val: 数值.
    :param rng: 范围.
    :param type_: 判断类型. '': 默认，正常判断. 'a': 方位角（度）.  'e' 俯仰角（度）.
    :return: 判断数值是否在范围内.
    """
    if rng is None:
        return True
    if type_ == '':
        c1 = (rng[0] is None) or (rng[0] is not None and rng[0] < val)
        c2 = (rng[1] is None) or (rng[1] is not None and val < rng[1])
        return c1 and c2
    elif type_ == 'a':
        val = val % 360
        b0, b1 = rng[0] % 360, rng[1] % 360
        if b1 >= b0:
            return b0 < val < b1
        else:
            return val < b0 or val > b1
    elif type_ == 'e':
        val = (val + 90) % 180 - 90
        b0, b1 = (rng[0] + 90) % 180 - 90, (rng[1] + 90) % 180 - 90
        return b0 < val < b1
    return False


##############################################################################
# 辅助类.
##############################################################################

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
