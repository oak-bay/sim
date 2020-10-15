import numpy as np
import math


def dim(v) -> int:
    """ 获取向量维度. """
    return len(v)


def vec(val):
    """ 数值向量化. """
    return np.array(val, dtype=np.float)


def dist(pos0, pos1=None) -> float:
    """ 计算向量距离（模）. """
    pos = (vec(pos0) - vec(pos1)) if pos1 is not None else vec(pos0)
    return np.linalg.norm(pos)


def unit(v):
    """ 计算单位向量. """
    v2 = vec(v)
    d = dist(v2)
    return (v2 / d) if d > 0.0 else zeros_like(v2)


def zeros_like(v):
    """ 生成全零向量. """
    return np.zeros_like(vec(v))


def angle(v1, v2) -> float:
    """ 计算向量夹角.
    """
    d1, d2 = dist(v1), dist(v2)
    if d1 <= 0.0 or d2 <= 0.0:
        return 0.0
    ret = math.acos(np.dot(v1, v2) / (d1 * d2))
    return math.degrees(ret)


def trans(v, *args):
    """ 坐标变换.
    对向量 v 依次用进行 m1, m2, ... 变换.

    :param v: 被变换向量.
    :param args: m1, m2, ...
    :return: 变换后的向量.
    """
    ret = v.copy()
    for m in args:
        mx = m.getA() if isinstance(m, np.matrix) else m
        ret = np.dot(mx, ret)
    return vec(ret)
