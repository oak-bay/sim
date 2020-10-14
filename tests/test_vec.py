import unittest
from sim.vec import *
import numpy as np


class TestVec(unittest.TestCase):
    def test_vec(self):
        v1 = vec([0, 0])
        self.assertTrue(type(v1) is np.ndarray)
        self.assertTrue(v1.dtype == np.float)

    def test_dist(self):
        v1 = vec([0, 0])
        v2 = vec([1, 1])
        v3 = vec([4, 5])
        self.assertAlmostEqual(dist(v2), 2 ** 0.5)
        self.assertAlmostEqual(dist(v3, v2), 5.0)
        self.assertAlmostEqual(dist(v1, v2), dist(v2, v1))

    def test_unit(self):
        v1 = vec([0, 0])
        v2 = vec([1, 1])
        self.assertTrue((unit(v2) == v2 / (2 ** 0.5)).all())
        self.assertTrue((unit(v2 - v1) == - unit(v1 - v2)).all())

    def test_angle(self):
        v1 = vec([0, 0])
        v2 = vec([1, 1])
        v3 = vec([1, 0])
        self.assertAlmostEqual(angle(v1, v2), 0.0)
        self.assertAlmostEqual(angle(v2, v3), 45.0)
        self.assertAlmostEqual(angle(v3, vec([0, 1])), 90.0)

    def test_trans(self):
        v1 = vec([1, 2])
        v2 = trans(v1, np.eye(2, dtype=np.float))
        np.testing.assert_almost_equal(v1, v2)

        v2 = trans(v1, np.mat([[1, 0], [0, 2]], dtype=np.float))
        np.testing.assert_almost_equal(v2, vec([1, 4]))
