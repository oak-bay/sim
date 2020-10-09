import unittest
import copy
from sim import Entity


class MockProp:
    pass


class MockEntity(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._copy_props += ['prop_a']
        self.prop_a = MockProp()
        self.prop_b = MockProp()


class MockEntity2(MockEntity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._copy_props += ['prop_b']


class TestEntity(unittest.TestCase):
    def test_basic(self):
        """ 测试基本功能. """
        obj = Entity()
        self.assertTrue(obj.id > 0)
        self.assertTrue(obj.env is None)

        ids = []
        for _ in range(100):
            obj = Entity()
            ids.append(obj.id)
        self.assertTrue(len(ids) == 100)

    def test_props(self):
        """ 测试动态属性. """
        obj = Entity(props={'a': 1, 'b': 2})
        self.assertTrue(hasattr(obj, 'a'))
        self.assertTrue(obj.a == 1)
        self.assertTrue(hasattr(obj, 'b'))
        self.assertTrue(obj.b == 2)
        self.assertTrue(not hasattr(obj, 'c'))

    def test_copy(self):
        """ 测试深拷贝. """
        obj = Entity()

        obj1 = MockEntity()
        obj2 = copy.deepcopy(obj1)
        self.assertNotEqual(id(obj1.prop_a), id(obj2.prop_a))
        self.assertEqual(id(obj1.prop_b), id(obj2.prop_b))
        self.assertNotEqual(id(obj._copy_props), id(obj1._copy_props))
        self.assertEqual(id(obj1._copy_props), id(obj1._copy_props))

        obj3 = MockEntity2()
        self.assertNotEqual(id(obj3._copy_props), id(obj1._copy_props))
