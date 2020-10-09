import numpy as np


def vec(val):
    """ 数值向量化. """
    return np.array(val, dtype=np.float)


def dist(pos0, pos1=None) -> float:
    """ 计算向量距离（模）. """
    if pos1 is None:
        return np.linalg.norm(vec(pos0))
    else:
        return np.linalg.norm(vec(pos1) - vec(pos0))


def unit(val):
    """ 计算单位向量. """
    val2 = vec(val)
    return val2 / dist(val2)


def zeros_like(val):
    """ 生成全零向量. """
    return np.zeros_like(vec(val))


def angle(v1, v2) -> float:
    """ 计算向量夹角.

    TODO: IMPLEMENT.
    """
    return 0.0
