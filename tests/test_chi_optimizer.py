# pylint: disable=missing-function-docstring
import unittest

from shapely.geometry import Point, Polygon

from optimizer import ChiOptimizer


# Test suite for pariwise reoptimization step
class chiOptimizerTest(unittest.TestCase):

    def test_simePolygon1(self):
        q = {0: Point(0.0, 0.0),
             1: Point(10.0, 0.0),
             2: Point(10.0, 1.0),
             3: Point(0.0, 1.0)}
        decomposition_ = [
            Polygon([(0.0, 0.0), (10.0, 0.0), (10.0, 0.5)], []),
            Polygon([(0.0, 0.0), (10.0, 0.5), (10.0, 1.0), (5.0,0.5)], []),
            Polygon([(5.0, 0.5), (10.0, 1.0), (0.0, 1.0)], []),
            Polygon([(0.0, 0.0), (5.0, 0.5), (0.0, 1.0)], [])]

        optimizer = ChiOptimizer()

        optimizer.run_iterations(decomposition=decomposition_,
                                 cell_to_site_map=q)

def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(chiOptimizerTest))
    return test_suite

mySuit = suite()
runner = unittest.TextTestRunner()
runner.run(mySuit)
