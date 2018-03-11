import unittest
from polygon_split import polygon_split

class polygonSplitTest(unittest.TestCase):

	def test_polygonSplit_emptyPolygon(self):
		P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
		e = [(0, 0), (1, 1)]
		self.assertEqual(polygon_split([], e), [])

	def test_polygonSplit_wrongFormatPolygon(self):
		P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
		e = [(0, 0), (1, 1)]
		self.assertEqual(polygon_split([[]], e), [])

	def test_polygonSplit_emptyEdge(self):
		P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
		e = [(0, 0), (1, 1)]
		self.assertEqual(polygon_split(P, []), [])

	def test_polygonSplit_emptyExterior(self):
		P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
		e = [(0, 0), (1, 1)]
		self.assertEqual(polygon_split([[], [1, 2, 3]], e), [])

	def test_polygonSplit_inccorrectEdge1(self):
		P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
		e = [(0, 0), (1, 1)]
		self.assertEqual(polygon_split(P, [(0, 0)]), [])

	def test_polygonSplit_inccorectEdge2(self):
		P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
		e = [(0, 0), (1, 1)]
		self.assertEqual(polygon_split(P, [(0, 0), (1, 1), (0, 1)]), [])

	def test_polygonSplit_selfintersectingPolygon(self):
		P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
		e = [(0, 0), (1, 1)]
		self.assertEqual(polygon_split([[(0, 0), (1, 0), (1, 1), (0.1, -0.1)], []], e), [])

	def test_polygonSplit_cutInsidePolygon(self):
		P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
		e = [(0, 0), (1, 1)]
		self.assertEqual(polygon_split(P, [(0.1, 0.1), (0.9, 0.9)]), [])

	def test_polygonSplit_cutTouchesPolygon(self):
		P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
		e = [(0, 0), (1, 1)]
		self.assertEqual(polygon_split(P, [(0, 0), (0.9, 0.9)]), [])

	def test_polygonSplit_cutAlongBoundary(self):
		P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
		e = [(0, 0), (1, 1)]
		self.assertEqual(polygon_split(P, [(0, 0), (0, 1)]), [])

	def test_polygonSplit_cutThroughManyPoints(self):
		P = [[(0, 0), (1, 0), (1, 1), (0.8, 1), (0.2, 0.8), (0.5, 1), (0, 1)], []]
		e = [(0.5, 0), (0.5, 1)]
		self.assertEqual(polygon_split(P, e), [])

	def test_polygonSplit_cutThroughHole(self):
		P = [[(0, 0), (1, 0), (1, 1), (0, 1)], [[(0.2, 0.2),
												(0.2, 0.8),
												(0.8, 0.8),
												(0.8, 0.2)]]]
		e = [(0.2, 0), (0.2, 1)]
		self.assertEqual(polygon_split(P, e), [])

	def test_polygonSplit_cutOutsidePolygon1(self):
		P = [[(0, 0), (0.5, 0.5), (1, 0), (1, 1), (0, 1)], []]
		e = [(0, 0), (1, 0)]
		self.assertEqual(polygon_split(P, e), [])

	def test_polygonSplit_cutOutsidePolygon2(self):
		P = [[(0, 0), (0.5, 0.5), (1, 0), (1, 1), (0, 1)], []]
		e = [(0, 0), (0.014, 1.1)]
		self.assertEqual(polygon_split(P, e), [])

	def test_polygonSplit_validSplit1(self):
		P = [[(0, 0), (1, 0), (1, 1), (0.8, 1), (0.2, 0.8), (0.5, 1), (0, 1)],
			[[(0.1, 0.1), (0.1, 0.2), (0.2, 0.1)],
			 [(0.9, 0.9), (0.9, 0.8), (0.8, 0.8)]]]
		e = [(0, 0), (0.2, 0.8)]
		result = polygon_split(P, e)
		self.assertTrue(result)
		P1, P2 = result
		self.assertTrue(P1)
		self.assertTrue(P2)
		self.assertEqual(set(P1[0]), set([(1.0, 0.0), (1.0, 1.0), (0.8, 1.0), (0.2, 0.8), (0.0, 0.0)]))
		self.assertEqual(set(P1[1][0]), set([(0.1, 0.1), (0.1, 0.2), (0.2, 0.1)]))
		self.assertEqual(set(P1[1][1]), set([(0.9, 0.9), (0.9, 0.8), (0.8, 0.8)]))
		self.assertEqual(set(P2[0]), set([(0.5, 1.0), (0.0, 1.0), (0.0, 0.0), (0.2, 0.8)]))

	def test_polygonSplit_validSplit2(self):
		P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
		e = [(0, 0.2), (1, 0.2)]
		result = polygon_split(P, e)
		self.assertTrue(result)
		P1, P2 = result
		self.assertTrue(P1)
		self.assertTrue(P2)
		self.assertEqual(set(P1[0]), set([(1.0, 0.0), (1.0, 0.2), (0.0, 0.2), (0.0, 0.0)]))
		self.assertEqual(set(P2[0]), set([(1.0, 1.0), (0.0, 1.0), (0.0, 0.2), (1.0, 0.2)]))

	def test_polygonSplit_validSplit3(self):
		P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
		e = [(0.2, 0), (0, 0.2)]
		result = polygon_split(P, e)
		self.assertTrue(result)
		P1, P2 = result
		self.assertTrue(P1)
		self.assertTrue(P2)
		self.assertEqual(set(P1[0]), set([(0.2, 0.0), (0.0, 0.2), (0.0, 0.0)]))
		self.assertEqual(set(P2[0]), set([(1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.2), (0.2, 0.0)]))

	def test_stability(self):
		P = [[(0, 0),
			  (3, 1),
			  (3, 0),
			  (4, 1),
			  (5, 0),
			  (5, 1),
			  (7, 1),
			  (5, 2),
			  (7, 3),
			  (0, 4),
			  (0, 2.5),
			  (1, 2),
			  (0, 1.5),
			  (1, 1),
			  (0, 0.5)], [[(3, 2), (3, 3), (4, 3), (4, 2)]]]
		
		from shapely.geometry import Polygon
		polyExterior = Polygon(*P).exterior
	
		from numpy import linspace
		from itertools import product
		searchDistances = list(linspace(0, polyExterior.length, 500))

		searchSpace = []
		for distance in searchDistances:
			solutionCandidate = polyExterior.interpolate(distance)
			searchSpace.append((solutionCandidate.x, solutionCandidate.y))
	
		try:
			for cutEdge in product(searchSpace, repeat=2):
				result = polygon_split(P, cutEdge)
		except Exception:
			self.fail("Stability test has failed!")



def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(polygonSplitTest))
    return test_suite

mySuit = suite()
runner = unittest.TextTestRunner()
runner.run(mySuit)