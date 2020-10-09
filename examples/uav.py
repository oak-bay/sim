from enum import Enum
import copy
from sim import Entity, Environment
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
            pass  # TODO: IMPLEMENT.
        self.control.take(actions)

    def is_alive(self) -> bool:
        c1 = self.control.state != UavState.OVER
        c2 = self.track.is_ok()
        c3 = not self.track.is_over()
        return c1 and c2 and c3


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
            pass
        elif self.state == UavState.RETURN:
            pass
        elif self.state == UavState.HOVER:
            pass

    def _update_conditions(self, actions):
        """ 判断状态. """
        self.C0 = self.uav.life < 0.0
        self.C3 = self.uav.track.is_over()
        self.C4 = self.uav.damage < 0.0

    def move(self, time_info):
        pos = copy.copy(self.uav.position)
        _, dt = time_info
        if self.state == UavState.FLY:
            pos = self._move_on_track(pos, self.uav.track, dt * self.uav.speed)
        self.uav.velocity = (pos - self.uav.position) / dt if dt > 0 else vec.zeros_like(pos)
        self.uav.position = pos

    def _move_on_track(self, pos, track, dist):
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


def print_entity_value(env: Environment):
    t, _ = env.time_info
    obj = env.children[0]
    if obj.is_alive():
        print(f'{t:.2f} : {obj.position} {obj.velocity}')
    else:
        print(f'{t:.2f} :')


if __name__ == "__main__":
    env = Environment()
    env.step_events.append(print_entity_value)
    uav = Uav(track=[[1, 1], [11, 1], [11, 11]], speed=2.5)
    env.add(uav)
    env.run()
    pass
