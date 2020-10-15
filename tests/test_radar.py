import unittest
from sim import vec, move
from sim.common.radar import Fov


class TestFov(unittest.TestCase):
    def test_mat_r(self):
        move.mat_r3z()

    def test_view(self):
        fov = Fov()

        obj_pos = vec.vec([0, 0, 1])
        ret = fov.view(obj_pos, pos=vec.vec([0, 0, 0]), dir_=[0, 0])
        self.assertTrue(ret is not None)
        print(ret)

        obj_pos = vec.vec([1, 0, 1])
        ret = fov.view(obj_pos, pos=vec.vec([0, 0, 0]), dir_=[0, 0])
        self.assertTrue(ret is not None)
        print(ret)

        obj_pos = vec.vec([0, 1, 1])
        ret = fov.view(obj_pos, pos=vec.vec([0, 0, 0]), dir_=[0, 0])
        self.assertTrue(ret is not None)
        print(ret)

