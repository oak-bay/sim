import copy
from .entity import Entity
from .env import Environment
from .move import MoveEntity
import matplotlib.pyplot as plt


class EntityPropRecorder:
    """ 属性记录. """

    def __init__(self, obj_tag, prop_name: str, show=False):
        self.obj_id = obj_tag if isinstance(obj_tag, int) else None
        self.obj = obj_tag if isinstance(obj_tag, Entity) else None
        self.prop_name = prop_name
        self.records = []
        self.show = show

    def __call__(self, env: Environment):
        if not self.obj:
            self.obj = env.find(self.obj_id)
        if self.obj:
            if hasattr(self.obj, self.prop_name):
                value = getattr(self.obj, self.prop_name)
                self.records.append(copy.copy(value))
                if self.show:
                    print(value)


class PropRecorder:
    """ 属性记录. """

    def __init__(self, prop_name: str, show=False):
        self.prop_name = prop_name
        self.records = {}
        self.show = show

    def __call__(self, env: Environment):
        for obj in env.children:
            if hasattr(obj, self.prop_name):
                if obj.id not in self.records:
                    self.records[obj.id] = []
                value = getattr(obj, self.prop_name)
                self.records[obj.id].append(copy.copy(value))
                if self.show:
                    print(f'{obj.id} : {value}')
