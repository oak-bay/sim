from typing import List, Optional
import copy


class EntityIdGen:
    """ 实体 ID 生成. """
    __id = 0

    @staticmethod
    def gen():
        EntityIdGen.__id += 1
        return EntityIdGen.__id


class Entity:
    """ 实体. """

    def __init__(self, **kwargs):
        self.__id = EntityIdGen.gen()
        self.env = None
        self._copy_props = []  # deepcopy 属性.
        if 'props' in kwargs:
            self._add_props(kwargs['props'])

    def _add_props(self, props):
        """ 支持动态属性. """
        if isinstance(props, dict):
            for k, v in props.items():
                if not hasattr(self, k):
                    setattr(self, k, v)

    def __deepcopy__(self, memodict={}):
        """ 对象深拷贝.

        为保证性能，采用策略：整体浅拷贝，保护值深拷贝.
        通过指定 _copy_props 属性，确认需要默认深拷贝的属性.
        """
        obj = copy.copy(self)
        for name in self._copy_props:
            if hasattr(self, name):
                v = copy.deepcopy(getattr(self, name))
                setattr(obj, name, v)
        return obj

    @property
    def id(self) -> int:
        """ 实体唯一标识号. """
        return self.__id

    def reset(self):
        pass

    def step(self, time_info):
        pass

    def access(self, others):
        pass

    def is_alive(self) -> bool:
        return True
