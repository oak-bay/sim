"""
雷达探测 UAV.
"""

from sim import Environment
from sim.common import Uav, Radar


if __name__ == '__main__':
    env = Environment()
    uav = env.add(Uav())
    radar = env.add(Radar())

    env.run()
