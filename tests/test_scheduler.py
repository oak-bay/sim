import unittest
from sim import Environment, EventScheduler


class Counter:
    def __init__(self):
        self.value = 0

    def __call__(self, env):
        self.value += 1


class TestScheduler(unittest.TestCase):
    def test_scheduler_fix(self):
        env = Environment()
        counter = Counter()
        env.step_events.append(EventScheduler(evt=counter, dt=0.1))
        env.run()
        self.assertTrue(counter.value == 101)

        counter2 = Counter()
        env.step_events.append(EventScheduler(evt=counter2, dt=0.2))
        env.run()
        self.assertTrue(counter2.value == 51)

    def test_scheduler_times(self):
        env = Environment()
        counter = Counter()
        env.step_events.append(EventScheduler(evt=counter, times=[1, 2, 5, 11]))
        env.run()
        self.assertTrue(counter.value == 3)

    def test_scheduler_rand(self):
        env = Environment()
        counter = Counter()
        env.step_events.append(EventScheduler(evt=counter, rand=[0.1, 1]))
        env.run()
        self.assertTrue(counter.value > 10)
