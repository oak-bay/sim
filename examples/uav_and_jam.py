from functools import partial
from sim import Entity, Environment
from sim.common import Uav, Jammer
from sim import EventScheduler


def print_uav_value(env: Environment, uav):
    t, _ = env.time_info
    if uav.is_alive():
        print(f'{t:.2f} : {uav.control.state} {uav.position} {uav.velocity}')
    else:
        print(f'{t:.2f} :')


def power_switch(env: Environment, jammer, on=None):
    t, _ = env.time_info
    if on is None:
        jammer.power_on = not jammer.power_on
    else:
        jammer.power_on = on
    print(f'{t:.2f} : jammer {jammer.power_on}')


if __name__ == "__main__":
    env = Environment()
    uav = env.add(Uav(track=[[1, 1], [11, 1], [11, 11]], speed=2.5))
    jammer1 = env.add(Jammer())
    jammer2 = env.add(Jammer(kind='gps'))

    uav_print = partial(print_uav_value, uav=uav)
    env.step_events.append(uav_print)

    # jammer1_switch = partial(power_switch, jammer=jammer1, on=None)
    # env.step_events.append(EventScheduler(evt=jammer1_switch, times=[2, 4]))

    jammer2_switch = partial(power_switch, jammer=jammer2, on=None)
    env.step_events.append(EventScheduler(evt=jammer2_switch, times=[3, 5]))

    env.run(stop=20)
    pass
