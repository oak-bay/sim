from enum import Enum
import copy
from functools import partial
from sim import Entity, Environment
from sim import EventScheduler
from sim import vec


class Uav(Entity):
    """ 无人机. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.control = UavControl(self)
        self.track = Track(**kwargs)
        self.life = 30.0
        self.speed = 3.0
        self.damage = 10.0
        self.position = None
        self.velocity = None
        self.rules = [rule_uav_jammer]
        self.set_params(**kwargs)
        self.reset()

    def set_params(self, **kwargs):
        if 'life' in kwargs and kwargs['life'] > 0.0:
            self.life = kwargs['life']
        if 'speed' in kwargs and kwargs['speed'] > 0.0:
            self.speed = kwargs['speed']

    def reset(self):
        if self.track.is_ok():
            self.position = self.track.start()
            self.velocity = vec.zeros_like(self.position)

    def step(self, time_info):
        _, dt = time_info
        self.control.move(time_info)
        self.life -= dt

    def access(self, others):
        actions = {}
        for other in others:
            for rule in self.rules:
                ret = rule(self, other)
                if ret is not None:
                    k, v = ret
                    if k not in actions:
                        actions[k] = []
                    actions[k].append(v)
        self.control.take(actions)

    def is_alive(self) -> bool:
        c1 = self.control.state != UavState.OVER
        c2 = self.track.is_ok()
        c3 = not self.track.is_over()
        return c1 and c2 and c3


def rule_uav_jammer(uav, jammer):
    if isinstance(jammer, Jammer):
        if jammer.power_on:
            return 'jam', 1
    return None


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


class UavState(Enum):
    """ 无人机状态. """
    START = 0  # 启动.
    FLY = 1  # 飞行.
    RETURN = 2  # 返航.
    HOVER = 3  # 悬停.
    OVER = 4  # 结束.


class UavControl:
    """ 无人机飞行控制.
    """

    def __init__(self, parent):
        self.uav = parent
        self.state = UavState.START
        self.C0 = False  # 电池耗尽
        self.C1 = False  # 测控被干扰
        self.C2 = False  # GPS被干扰（无输出）
        self.C3 = False  # 航路飞完
        self.C4 = False  # 机体损坏

    def take(self, actions):
        """ 根据接收动作，更新状态机.

        TODO: 更新状态表.
        """
        self._update_conditions(actions)
        if self.state == UavState.START:
            if self.C0 or self.C4:
                self.state = UavState.OVER
            elif self.C1 or self.C2:
                self.state = UavState.START
            else:
                self.state = UavState.FLY
        elif self.state == UavState.FLY:
            if self.C0 or self.C3 or self.C4:
                self.state = UavState.OVER
            elif self.C1 or self.C2:
                self.state = UavState.HOVER
        elif self.state == UavState.RETURN:
            if self.C0 or self.C4:
                self.state = UavState.OVER
            elif self.C1 and not self.C2:
                self.state = UavState.RETURN
            else:
                self.state = UavState.HOVER
        elif self.state == UavState.HOVER:
            if self.C0 or self.C4:
                self.state = UavState.OVER
            elif self.C2:
                self.state = UavState.HOVER
            elif self.C1 and not self.C2:
                self.state = UavState.RETURN
            elif not (self.C1 or self.C2 or self.C3):
                self.state = UavState.FLY

    def _update_conditions(self, actions):
        """ 判断状态. """
        self.C0 = self.uav.life < 0.0
        self.C1 = 'jam' in actions
        self.C2 = 'gps' in actions
        self.C3 = self.uav.track.is_over()
        self.C4 = self.uav.damage < 0.0

    def move(self, time_info):
        pos = copy.copy(self.uav.position)
        _, dt = time_info
        if self.state == UavState.FLY:
            pos = move_on_track(pos, self.uav.track, dt * self.uav.speed)
        elif self.state == UavState.RETURN:
            pos, _ = move_to(pos, self.uav.track.start(), dt * self.uav.speed)
        self.uav.velocity = (pos - self.uav.position) / dt if dt > 0 else vec.zeros_like(pos)
        self.uav.position = pos


def print_uav_value(env: Environment, uav):
    t, _ = env.time_info
    if uav.is_alive():
        print(f'{t:.2f} : {uav.control.state} {uav.position} {uav.velocity}')
    else:
        print(f'{t:.2f} :')


class Jammer(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.power_on = False


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
    jammer = env.add(Jammer())

    print_uav = partial(print_uav_value, uav=uav)
    env.step_events.append(print_uav)
    switch = partial(power_switch, jammer=jammer, on=None)
    env.step_events.append(EventScheduler(evt=switch, times=[2, 3]))

    env.run()
    pass
