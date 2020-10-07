from enum import Enum


class Uav:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.control = UavControl(self)
        self.life = 30.0
        self.damage = 10.0


class UavState(Enum):
    START = 0
    FLY = 1
    RETURN = 2
    HOVER = 3
    OVER = 4


class UavControl:
    def __init__(self, uav):
        self.uav = uav
        self.state = UavState.START
        self.C0 = False
        self.C1 = False
        self.C2 = False
        self.C3 = False
        self.C4 = False

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
        self.C4 = self.uav.damage < 0.0

    def move(self):
        if self.state == UavState.START:
            pass
        elif self.state == UavState.FLY:
            pass
        elif self.state == UavState.RETURN:
            pass
        elif self.state == UavState.HOVER:
            pass


if __name__ == "__main__":
    uav = Uav()
