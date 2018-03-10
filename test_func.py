import unittest
from polygon_split import polygon_split

class unitTest(unittest.TestCase):

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



if __name__ == '__main__':
	unittest.main()
