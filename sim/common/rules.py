from .jammer import Jammer


def rule_uav_jammer(uav, jammer):
    """ UAV 与 Jammer 交互规则. """
    if isinstance(jammer, Jammer):
        if jammer.power_on:
            return jammer.kind, 1
    return None
