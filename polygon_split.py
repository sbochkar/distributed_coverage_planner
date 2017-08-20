from shapely.geometry import Point
from shapely.geometry import MultiPoint
from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import LinearRing


def pretty_print_poly(P=[]):
	"""Pretty prints cannonical polygons to help with debugging

	Args:
		P: Polygon in canonical form.

	Returns:
		None
	"""

	print("Polygon:\n\tExterior:\n\t\t"),

	for pts in P[0]:
		# Need to make sure to round some pts for nice display
		print("(%3.1f, %3.1f), "%(pts[0], pts[1])),
	print("")
	holeCnt = 0
	for hole in P[1]:
		print("\tHole %d:\n\t\t"%holeCnt),
		for pts in hole:
			# Need to make sure to round some pts for nice display
			print("(%3.1f, %3.1f),"%(pts[0], pts[1])),
		print("")
		holeCnt += 1


def inputs_valid(polygon=[], splitLine=[]):
	""" Quick function to check validity of inputs

	Perform a variety of checks to make sure we only admit valid inputs.
	This is mainly to ensure as much robsutness as possible. In the past, not
	having these checks have lead to a number of problems.

	Args:
		polygon: Polygon in the form of [ [], [[],...] ] where polygon[0] is
			the exterior boundary of the polygon and polygon[1] is the list
			of boundaries of holes.
			Exterior boundary must be in ccw order. Last point != first point.
			Same for hole boundaries.
		splitLine: A line along which to split polygon into two. A list of 2
			tuples specifying coordinates of straight line

	Returns:
		True: If inputs are valid. Useful constructs otherwise.
	"""


	global DEBUG_LEVEL

	# We are very much interesting in rebustness, so performing sanity checks.
	if not splitLine:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested on an empty split line.")

		return False

	if len(splitLine) != 2:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested on an split line with wrong number \
										 of coordinates.")

		return False

	if not polygon or len(polygon) != 2:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested on a polygon of wrong format.")

		return False


	extr, holes = polygon

	if not extr:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested on a polygon with empty exterior.")

		return False

	pPol = Polygon(*polygon)

	if not pPol.is_valid:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested on an invalid polygon.")

		return False

	return True


def parameters_valid(common_pts=[], holes=[], splitLineLS=[]):
	""" Quick function to check validity of some interim variable of the algo

	Perform a variety of checks to make sure we only admit valid inputs.
	This is mainly to ensure as much robsutness as possible. In the past, not
	having these checks have lead to a number of problems.

	Args:
		common_pts: Points resulted in intersection of split line and boundary.
			Should be MultiPoint object.
		holes: Hole boundaries of the original polygon.
		splitLineLS: LineString object representing the split line.

	Returns:
		True: If paramters are valid. False otherwise.
	"""

	if not common_pts:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested but split line is within a polygon.")

		return False

	if type(common_pts) is not MultiPoint:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested but split line is not valid.")

		return False

	if len(common_pts) > 2:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested but split line crosses many times.")

		return False

	for hole in holes:
		holeLS = LinearRing(hole)

		if splitLineLS.intersects(holeLS):
			if DEBUG_LEVEL & 0x04:
				print("Polygon split requested but split line crosses a hole.")

			return False

	return True


def convert_to_canonical(P=[]):
	"""Convertion function to convert from shapely object to canonical form.

	Args:
		P: Shapely object representing a polygon.

	Returns:
		poly: A polygon represented in canonical form. [] otherwise.
	"""

	if type(P) is not Polygon:
		if DEBUG_LEVEL & 0x04:
			print("Polygon conversion requested but wrong input specified.")

			return []

	poly = [[], []]

	if not LinearRing(P.exterior.coords).is_ccw:
		poly[0] = list(P.exterior.coords)[::-1][:-1]
	else:
		poly[0] = list(P.exterior.coords)[:-1]

	for hole in P.interiors:

		if LinearRing(hole.coords).is_ccw:
			poly[1].append(list(hole.coords)[::-1][:-1])
		else:
			poly[1].append(list(hole.coords)[:-1])

	return poly


def polygon_split(polygon=[], splitLine=[]):
	"""Split a polygon into two other polygons along splitLine.

	Attempts to split a polygon into two other polygons. Here, a number of
	assumptions has to be made. That is, that splitLine is a proper line
	connecting 	boundaries of a polygon. Also, that splitLine does not connect
	outside boundary to a boundary of hole. This is a undefined behaviour.

	TODO: With current implementation, it may be possible to do non-decomposing
		cuts. But, some thought needs to be put in.
	TODO: Consider returning Shapely objects instead of converting them to
		canonical form. Will improve cycle efficiency.

	Args:
		polygon: Polygon in the form of [ [], [[],...] ] where polygon[0] is
			the exterior boundary of the polygon and polygon[1] is the list
			of boundaries of holes.
			Exterior boundary must be in ccw order. Last point != first point.
			Same for hole boundaries.
		splitLine: A line along which to split polygon into two. A list of 2
			tuples specifying coordinates of straight line

	Returns:
		(P1, P2): A tuple of polygons resulted from the split. If error occured,
		returns [].

	"""


	global DEBUG_LEVEL


	if not inputs_valid(polygon, splitLine):
		return []

	extr, holes = polygon
	pPol = Polygon(*polygon)

	splitLineLS = LineString(splitLine)
	extrLineLR = LinearRing(extr)

	# This calculates the points on the boundary where the split will happen.
	common_pts = extrLineLR.intersection(splitLineLS)

	if not parameters_valid(common_pts, holes, splitLineLS):
		return []

	splitBoundary = extrLineLR.difference(splitLineLS)

	# Sanity check to make sure we get the right result
	if type(splitBoundary) is not MultiLineString and len(splitBoundary) != 2:
		if DEBUG_LEVEL & 0x04:
			print("Polygon split requested but boundary split is invalid.")

		return []

	mask1 = Polygon(splitBoundary[0])
	mask2 = Polygon(splitBoundary[1])

	resP1Pol = pPol.intersection(mask1)
	resP2Pol = pPol.intersection(mask2)

	# The results of the intersection are Shapely objects. Convert them to list.
	resP1 = convert_to_canonical(resP1Pol)
	resP2 = convert_to_canonical(resP2Pol)

	return resP1, resP2


if __name__ == '__main__':

	# If package is launched from cmd line, run sanity checks
	DEBUG_LEVEL = 0

	P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
	e = [(0, 0), (1, 1)]

	result = "PASS" if not polygon_split([], e) else "FAIL"
	print("[%s] Empty P test."%result)

	result = "PASS" if not polygon_split([[]], e) else "FAIL"
	print("[%s] Wrong P format test."%result)

	result = "PASS" if not polygon_split(P, []) else "FAIL"
	print("[%s] Empty e test."%result)

	result = "PASS" if not polygon_split([[], [1, 2, 3]], e) else "FAIL"
	print("[%s] Empty exterior of P test."%result)

	result = "PASS" if not polygon_split(P, [(0, 0)]) else "FAIL"
	print("[%s] Split line with one coordinate."%result)

	result = "PASS" if not polygon_split(P, [(0, 0), (1, 1), (0, 1)]) else "FAIL"
	print("[%s] Split line with 3 coordinate."%result)

	result = "PASS" if not polygon_split([[(0, 0), (1, 0), (1, 1), (0.1, -0.1)], []], e) else "FAIL"
	print("[%s] Invalid polygon test."%result)

	result = "PASS" if not polygon_split(P, [(0.1, 0.1), (0.9, 0.9)]) else "FAIL"
	print("[%s] Cut entirely within polygon."%result)

	result = "PASS" if not polygon_split(P, [(0, 0), (0.9, 0.9)]) else "FAIL"
	print("[%s] Split line touches boundary at one point."%result)

	result = "PASS" if not polygon_split(P, [(0, 0), (0, 1)]) else "FAIL"
	print("[%s] Split line is along a boundary."%result)

	P = [[(0, 0), (1, 0), (1, 1), (0.8, 1), (0.2, 0.8), (0.5, 1), (0, 1)], []]
	e = [(0.5, 0), (0.5, 1)]
	result = "PASS" if not polygon_split(P, e) else "FAIL"
	print("[%s] Split line crosses more than 2 points."%result)

	P = [[(0, 0), (1, 0), (1, 1), (0, 1)], [[(0.2, 0.2),
											 (0.2, 0.8),
											 (0.8, 0.8),
											 (0.8, 0.2)]]]
	e = [(0.2, 0), (0.2, 1)]
	result = "PASS" if not  polygon_split(P, e) else "FAIL"
	print("[%s] Split line crosses a hole."%result)

	# Now, do actual functional tests
	P = [[(0, 0), (1, 0), (1, 1), (0.8, 1), (0.2, 0.8), (0.5, 1), (0, 1)],
			[[(0.1, 0.1), (0.1, 0.2), (0.2, 0.1)],
			 [(0.9, 0.9), (0.9, 0.8), (0.8, 0.8)]]]
	e = [(0, 0), (0.2, 0.8)]
	P1, P2 = polygon_split(P, e)
	result = "PASS"
	if set(P1[0]) != set([(1.0, 0.0), (1.0, 1.0), (0.8, 1.0), (0.2, 0.8), (0.0, 0.0)]):
		result = "FAIL"
	if set(P1[1][0]) != set([(0.1, 0.1), (0.1, 0.2), (0.2, 0.1)]):
		result = "FAIL"
	if set(P1[1][1]) != set([(0.9, 0.9), (0.9, 0.8), (0.8, 0.8)]):
		result = "FAIL"
	if set(P2[0]) != set([(0.5, 1.0),  (0.0, 1.0),  (0.0, 0.0),  (0.2, 0.8)]):
		result = "FAIL"
	print("[%s] Simple valid split test."%result)

	pretty_print_poly(P2)