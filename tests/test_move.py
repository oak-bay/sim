import unittest
import numpy as np
from sim import vec, move


class TestMove(unittest.TestCase):
    def test_xyz_aer(self):
        """ 测试 XYZ 和 AER 之间的坐标转换.
        1.xyz_to_aer
        2.aer_to_xyz
        """
        xyz = vec.vec([1, 1, 1])
        aer = move.xyz_to_aer(xyz)
        xyz2 = move.aer_to_xyz(aer)
        np.testing.assert_almost_equal(xyz, xyz2)

        xyz = vec.vec([0, 0, 0])
        aer = move.xyz_to_aer(xyz)
        xyz2 = move.aer_to_xyz(aer)
        np.testing.assert_almost_equal(xyz, xyz2)

        xyz = vec.vec([1, 2, 3])
        aer = move.xyz_to_aer(xyz)
        xyz2 = move.aer_to_xyz(aer)
        np.testing.assert_almost_equal(xyz, xyz2)

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
