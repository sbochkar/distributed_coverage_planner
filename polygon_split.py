from shapely.geometry import Point
from shapely.geometry import MultiPoint
from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import LinearRing


# Arbitrarily small epsilon for buffer operations
BUFFER_EPS = 10e-06


def polygon_split(polygon=[], split_line=[]):
	"""Split a polygon into two other polygons along split_line

	Attempts to split a polygon into two other polygons. Here, a number of
	assumptions has to be made. That is, that split_line is a proper line
	connecting 	boundaries of a polygon. Also, that split_line does not connect
	outside boundary to a boundary of hole. This is a undefined behaviour.

	TODO: With current implementation, it may be possible to do non-decomposing
		cuts. But, some work needs to be put in to it. For now, it's underfined.

	Args:
		polygon: Polygon in the form of [ [], [[],...] ] where polygon[0] is
			the exterior boundary of the polygon and polygon[1] is the list
			of boundaries of holes.
			Exterior boundary must be in ccw order. Last point != first point.
			Same for hole boundaries.
		split_line: A line along which to split polygon into two. A list of 2
			tuples specifying coordinates of straight line

	Returns:
		(P1, P2): A tuple of polygons resulted from the split. If error occured,
		returns [].

	"""


	global DEBUG_LEVEL

	# We are very much interesting in rebustness, so performing sanity checks.
	if not split_line:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested on an empty split line.")

		return []

	if len(split_line) != 2:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested on an split line with wrong number \
										 of coordinates.")

		return []


	if not polygon or len(polygon) != 2:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested on a polygon of wrong format.")

		return []


	extr, holes = polygon
	if not extr:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested on a polygon with empty exterior.")

		return []

	pPol = Polygon(*polygon)
	if not pPol.is_valid:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested on an invalid polygon.")

		return []


	splitLineLS = LineString(split_line)
	extrLineLR = LinearRing(extr)

	common_pts = extrLineLR.intersection(splitLineLS)

	if not common_pts:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested but split line is within a polygon.")

		return []

	if type(common_pts) is not MultiPoint:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested but split line is not valid.")

		return []

	if len(common_pts) > 2:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested but split line crosses many times.")

		return []

	for hole in holes:
		holeLS = LinearRing(hole)

		if splitLineLS.intersects(holeLS):
			if DEBUG_LEVEL & 0x04:
				print("Polygon split requested but split line crosses a hole.")

			return []

	splitBoundary = extrLineLR.difference(splitLineLS)
	if type(splitBoundary) is not MultiLineString and len(splitBoundary) != 2:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested but boundary split is invalid.")

		return []

	mask1 = Polygon(splitBoundary[0])
	mask2 = Polygon(splitBoundary[1])

	res_P1 = pPol.intersection(mask1)
	res_P2 = pPol.intersection(mask2)

	return res_P1, res_P2


if __name__ == '__main__':

	# If package is launched from cmd line, run sanity checks
	DEBUG_LEVEL = 0

	P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
	e = [(0, 0), (1, 1)]

	result = polygon_split([], e)
	if not result:
		print("[PASSED] Empty P test.")
	else:
		print("[FAILED] Empty P test.")

	result = polygon_split([[]], e)
	if not result:
		print("[PASSED] Wrong P format test.")
	else:
		print("[FAILED] Wrong P format test.")

	result = polygon_split(P, [])
	if not result:
		print("[PASSED] Empty e test.")
	else:
		print("[FAILED] Empty e test.")

	result = polygon_split([[], [1, 2, 3]], e)
	if not result:
		print("[PASSED] Empty exterior of P test.")
	else:
		print("[FAILED] Empty exterior of P test.")

	result = polygon_split(P, [(0, 0)])
	if not result:
		print("[PASSED] Split line with one coordinate.")
	else:
		print("[FAILED] Split line with one coordinate.")

	result = polygon_split(P, [(0, 0), (1, 1), (0, 1)])
	if not result:
		print("[PASSED] Split line with one coordinate.")
	else:
		print("[FAILED] Split line with 3 coordinates.")

	result = polygon_split([[(0, 0), (1, 0), (1, 1), (0.1, -0.1)], []], e)
	if not result:
		print("[PASSED] Invalid polygon test.")
	else:
		print("[FAILED] Invalid polygon test.")

	result = polygon_split(P, [(0.1, 0.1), (0.9, 0.9)])
	if not result:
		print("[PASSED] Cut entirely within polygon.")
	else:
		print("[FAILED] Cut entirely within polygon.")

	result = polygon_split(P, [(0, 0), (0.9, 0.9)])
	if not result:
		print("[PASSED] Split line touches boundary at one point.")
	else:
		print("[FAILED] Split line touches boundary at one point.")

	result = polygon_split(P, [(0, 0), (0, 1)])
	if not result:
		print("[PASSED] Split line is along a boundary.")
	else:
		print("[FAILED] Split line is along a boundary.")

	P = [[(0, 0), (1, 0), (1, 1), (0.8, 1), (0.2, 0.8), (0.5, 1), (0, 1)], []]
	e = [(0.5, 0), (0.5, 1)]
	result =  polygon_split(P, e)
	if not result:
		print("[PASSED] Split line crosses more than 2 points.")
	else:
		print("[FAILED] Split line crosses more than 2 points.")

	P = [[(0, 0), (1, 0), (1, 1), (0, 1)], [[(0.2, 0.2),
											 (0.2, 0.8),
											 (0.8, 0.8),
											 (0.8, 0.2)]]]
	e = [(0.2, 0), (0.2, 1)]
	result =  polygon_split(P, e)
	if not result:
		print("[PASSED] Split line crosses a hole.")
	else:
		print("[FAILED] Split line crosses a hole.")

	# Now, do actual functional tests



	P = [[(0, 0), (1, 0), (1, 1), (0.8, 1), (0.2, 0.8), (0.5, 1), (0, 1)],
			[[(0.1, 0.1), (0.1, 0.2), (0.2, 0.1)],
			 [(0.9, 0.9), (0.9, 0.8), (0.8, 0.8)]]]
	e = [(0, 0), (0.2, 0.8)]
	print(polygon_split(P, e))


	P = [[(0, 0), (1, 0), (1, 1), (0, 1)], [[(0.25, 0.25), (0.25, 0.75), (0.75, 0.75), (0.75, 0.25)]]]