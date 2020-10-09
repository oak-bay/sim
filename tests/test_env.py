import unittest

from sim import Environment, Entity


class MockEntity(Entity):
    """ 模拟实体. """

    def __init__(self):
        super().__init__()
        self.value = 0

    def step(self, time_info):
        self.value += 1

    def reset(self):
        self.value = 0

    def access(self, others):
        for _ in others:
            self.value -= 0.5


class MockEvent:
    """ 模拟步进事件对象. """

    def __init__(self):
        self.time_records = []

    def __call__(self, env: Environment):
        now, _ = env.time_info
        self.time_records.append(now)


class TestEnv(unittest.TestCase):
    """ 环境对象测试. """

    def test_entity_management(self):
        """ 测试对象管理. """
        env = Environment()

        obj1 = env.add(Entity())
        obj2 = env.add(obj1)
        self.assertTrue(obj1 is obj2)
        self.assertTrue(obj1.env is env)
        self.assertTrue(len(env.children) == 1)

        obj3 = env.add(Entity())
        self.assertTrue(obj3.env is env)
        self.assertTrue(len(env.children) == 2)

        env.remove(obj1)
        self.assertTrue(obj1.env is None)
        self.assertTrue(len(env.children) == 1)

        env.remove(obj3)
        self.assertTrue(len(env.children) == 0)

    def test_entity_find(self):
        """ 测试对象搜索. """
        env = Environment()

        obj1 = env.add(Entity(name='tom'))
        obj2 = env.find(obj1)
        self.assertTrue(obj2 is obj1)
        obj2 = env.find(obj1.id)
        self.assertTrue(obj2 is obj1)

        obj2 = env.find(obj1.id + 1)
        self.assertTrue(obj2 is None)

        obj2 = env.find('tom')
        self.assertTrue(obj2 is not None)

        obj2 = env.find('jerry')
        self.assertTrue(obj2 is None)

    def test_run(self):
        """ 测试运行. """
        env = Environment()

        env.run(stop=20.0)
        self.assertAlmostEqual(env.time_info[0], 20.0)
        env.run(stop=30.0)
        self.assertAlmostEqual(env.time_info[0], 30.0)
        env.run()
        self.assertAlmostEqual(env.time_info[0], 30.0)

        obj = env.add(MockEntity())
        env.run(stop=10.0)
        self.assertTrue(obj.value == 101)

        env.run(stop=10.0, step=1.0)
        self.assertTrue(obj.value == 11)

        env.run(start=5.0, stop=10.0, step=0.1)
        self.assertTrue(obj.value == 51)

    def test_step_event(self):
        """ 测试运行事件. """
        env = Environment()

        evt = MockEvent()
        env.step_events.append(evt)

        env.run()
        self.assertAlmostEqual(evt.time_records[0], 0.0)
        self.assertAlmostEqual(evt.time_records[-1], 10.0)

    def test_access(self):
        env = Environment()

        obj1 = env.add(MockEntity())
        obj2 = env.add(MockEntity())

        env.run()

        self.assertAlmostEqual(obj1.value, 101.0 / 2)
        self.assertAlmostEqual(obj2.value, 101.0 / 2)
