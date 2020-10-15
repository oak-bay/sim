"""
雷达探测 UAV.
"""

from sim import Environment
from sim.common import Uav, Radar
from sim import EventScheduler
from functools import partial


def print_time(env: Environment):
    t, _ = env.time_info
    print(f'{t:.2f} : --------------------------------------------------')


def print_uav_value(env: Environment, uav: Uav):
    t, _ = env.time_info
    if uav.is_alive():
        print(f'{t:.2f} : Uav-{uav.id} - {uav.control.state} {uav.position} {uav.velocity}')


def print_radar_value(env: Environment, radar: Radar):
    t, _ = env.time_info
    if radar.current_results:
        print(f'{t:.2f} : Radar-{radar.id} - {radar.current_results}')


if __name__ == '__main__':
    env = Environment()
    env.step_events.append(print_time)

    uav = env.add(Uav(track=[[0, 100, 10], [100, 100, 10]], speed=2.5))
    env.step_events.append(partial(print_uav_value, uav=uav))

    # uav2 = env.add(Uav(track=[[0, 0, 10], [10, 10, 10]], speed=2.5))
    # env.step_events.append(partial(print_uav_value, uav=uav2))

    radar = env.add(Radar(pos=[0, 0, 0], out='ar', rate=2, r_range=[None, 150]))
    env.step_events.append(partial(print_radar_value, radar=radar))

    env.run(stop=40)
