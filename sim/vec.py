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
    val2 = vec(val)
    return val2 / dist(val2)
