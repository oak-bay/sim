import unittest
import numpy as np
import math
from sim import vec, move


class TestMove(unittest.TestCase):
    def test_xyz_aer(self):
        """ 测试 XYZ 和 AER 之间的坐标转换.
        1.xyz_to_aer
        2.aer_to_xyz
        """
        xyz = vec.vec([1, 0, 0])
        aer = move.xyz_to_aer(xyz)
        np.testing.assert_almost_equal(aer, vec.vec([90, 0, 1]))
        xyz2 = move.aer_to_xyz(aer)
        np.testing.assert_almost_equal(xyz, xyz2)

        xyz = vec.vec([0, 1, 0])
        aer = move.xyz_to_aer(xyz)
        np.testing.assert_almost_equal(aer, vec.vec([0, 0, 1]))
        xyz2 = move.aer_to_xyz(aer)
        np.testing.assert_almost_equal(xyz, xyz2)

        xyz = vec.vec([-1, 0, 0])
        aer = move.xyz_to_aer(xyz)
        np.testing.assert_almost_equal(aer, vec.vec([270, 0, 1]))
        xyz2 = move.aer_to_xyz(aer)
        np.testing.assert_almost_equal(xyz, xyz2)

        xyz = vec.vec([0, 1, 1])
        aer = move.xyz_to_aer(xyz)
        np.testing.assert_almost_equal(aer, vec.vec([0, 45, 2 ** 0.5]))
        xyz2 = move.aer_to_xyz(aer)
        np.testing.assert_almost_equal(xyz, xyz2)

        xyz = vec.vec([0, 1, -1])
        aer = move.xyz_to_aer(xyz)
        np.testing.assert_almost_equal(aer, vec.vec([0, -45, 2 ** 0.5]))
        xyz2 = move.aer_to_xyz(aer)
        np.testing.assert_almost_equal(xyz, xyz2)

        xyz = vec.vec([1, 2, 3])
        aer = move.xyz_to_aer(xyz, angle='r')
        xyz2 = move.aer_to_xyz(aer, angle='r')
        np.testing.assert_almost_equal(xyz, xyz2)

        aer = move.xyz_to_aer(xyz, angle='d')
        xyz2 = move.aer_to_xyz(aer, angle='d')
        np.testing.assert_almost_equal(xyz, xyz2)

    def test_move_to(self):
        """ 测试移动函数.
        1. move_to
        """
        pt0 = vec.vec([0, 0])
        pt1 = vec.vec([0, 1])

        pt2, d = move.move_to(pt0, pt1, 0.5)
        np.testing.assert_almost_equal(pt2, vec.vec([0, 0.5]))
        self.assertAlmostEqual(d, 0.5)

        pt2, d = move.move_to(pt0, pt1, 1)
        np.testing.assert_almost_equal(pt2, vec.vec([0, 1]))
        self.assertAlmostEqual(d, 0)

        pt2, d = move.move_to(pt0, pt1, 1.5)
        np.testing.assert_almost_equal(pt2, vec.vec([0, 1]))
        self.assertAlmostEqual(d, -0.5)

    def test_in_range(self):
        self.assertTrue(move.in_range(2, [1, 3]))
        self.assertTrue(move.in_range(2, [None, 3]))
        self.assertTrue(not move.in_range(4, [None, 3]))
        self.assertTrue(move.in_range(2, [1, None]))
        self.assertTrue(not move.in_range(2, [3, None]))
        self.assertTrue(not move.in_range(0, [1, 3]))
        self.assertTrue(not move.in_range(4, [1, 3]))

        self.assertTrue(move.in_range(45, [0, 90], type_='a'))
        self.assertTrue(move.in_range(45, [360, 90], type_='a'))
        self.assertTrue(not move.in_range(100, [0, 90], type_='a'))
        self.assertTrue(move.in_range(0, [270, 90], type_='a'))
        self.assertTrue(move.in_range(0, [270, 450], type_='a'))

        self.assertTrue(move.in_range(30, [0, 45], type_='e'))
        self.assertTrue(not move.in_range(50, [0, 45], type_='e'))

    def test_mat_a(self):
        v = vec.vec([0, 1])

        m = move.mat_a(00)
        v2 = vec.trans(v, m)
        np.testing.assert_almost_equal(v2, vec.vec([0, 1]))

        m = move.mat_a(90)
        v2 = vec.trans(v, m)
        np.testing.assert_almost_equal(v2, vec.vec([-1, 0]))

        m = move.mat_a(180)
        v2 = vec.trans(v, m)
        np.testing.assert_almost_equal(v2, vec.vec([0, -1]))

        m = move.mat_a(270)
        v2 = vec.trans(v, m)
        np.testing.assert_almost_equal(v2, vec.vec([1, 0]))

    def test_mat_ae(self):
        """ 测试 mat_ae """
        v = vec.vec([0, 1, 0])

        m = move.mat_ae([0, 0])
        v2 = vec.trans(v, m)
        np.testing.assert_almost_equal(v2, vec.vec([0, 1, 0]))

        m = move.mat_ae([90, 0])
        v2 = vec.trans(v, m)
        np.testing.assert_almost_equal(v2, vec.vec([-1, 0, 0]))

        m = move.mat_ae([180, 0])
        v2 = vec.trans(v, m)
        np.testing.assert_almost_equal(v2, vec.vec([0, -1, 0]))

        m = move.mat_ae([270, 0])
        v2 = vec.trans(v, m)
        np.testing.assert_almost_equal(v2, vec.vec([1, 0, 0]))

        """ 测试俯仰. """
        v = vec.vec([0, 2 ** 0.5, 0])
        m = move.mat_ae([0, -45])
        v2 = vec.trans(v, m)
        np.testing.assert_almost_equal(v2, vec.vec([0, 1, 1]))

        m = move.mat_ae([0, 45])
        v2 = vec.trans(v, m)
        np.testing.assert_almost_equal(v2, vec.vec([0, 1, -1]))

        """ 综合测试. """
        v = vec.vec([0, 2 ** 0.5, 0])
        m = move.mat_ae([90, 45])
        np.testing.assert_almost_equal(v2, vec.vec([-1, 0, -1]))
