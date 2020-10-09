import copy
from sim import Entity, Environment


class EntityPropRecorder:
    """ 实体+属性 记录. """

    def __init__(self, obj_tag, prop_name: str, show=False, alive=True, not_none=True):
        """ 初始化.

        :param obj_tag: 实体标签.
        :param prop_name: 属性名称.
        :param show: 是否显示.
        :param alive: 是否只记录活动状态.
        :param not_none: 是否只记录非 None 值.
        """
        self.obj_id = obj_tag if isinstance(obj_tag, int) else None
        self.obj = obj_tag if isinstance(obj_tag, Entity) else None
        self.prop_name = prop_name
        self.records = []
        self.show = show
        self.alive = alive
        self.not_none = not_none

    def __call__(self, env: Environment):
        if not self.obj:
            self.obj = env.find(self.obj_id)
        if self.obj and (self.obj.is_alive() if self.alive else True):
            if hasattr(self.obj, self.prop_name):
                value = getattr(self.obj, self.prop_name)
                if self.not_none and value is None:
                    return
                self.records.append(copy.copy(value))
                if self.show:
                    print(f'{env.time_info[0]:.2f} - {self.obj.id} : {value}')


class PropRecorder:
    """ 属性记录. """

    def __init__(self, prop_name: str, show=False, alive=True):
        """ 初始化.

        :param prop_name: 属性名称.
        :param show: 是否显示.
        """
        self.prop_name = prop_name
        self.records = {}
        self.show = show
        self.alive = alive

    def __call__(self, env: Environment):
        for obj in env.children:
            if hasattr(obj, self.prop_name) and (obj.is_alive() if self.alive else True):
                if obj.id not in self.records:
                    self.records[obj.id] = []
                value = getattr(obj, self.prop_name)
                self.records[obj.id].append(copy.copy(value))
                if self.show:
                    print(f'{env.time_info[0]:.2f} - {obj.id} : {value}')
