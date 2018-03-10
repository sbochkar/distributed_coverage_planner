import logging

from shapely.geometry import Point
from shapely.geometry import MultiPoint
from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import LinearRing


# Configure logging properties for this module
logger = logging.getLogger("polygonSplit")
fileHandler = logging.FileHandler("polygonSplit.log")
streamHandler = logging.StreamHandler()
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)
logger.setLevel(logging.INFO)


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


def convert_to_canonical(P=[]):
	"""Convertion function to convert from shapely object to canonical form.

	Args:
		P: Shapely object representing a polygon.

	Returns:
		poly: A polygon represented in canonical form. [] otherwise.
	"""

	if type(P) is not Polygon:
		logger.warn("Polygon conversion requested but wrong input specified.")
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

	# Empty splitLine test
	if not splitLine:
		return []
	# Empty polygon test
	if not polygon:
		return [] 
	# Validity of splitLine
	if len(splitLine) != 2:
		return []
	# Validity of polygon
	if len(polygon) != 2:
		return []

	extr, holes = polygon

	# Validity of exterior of polygon
	if not extr:
		return []


	pPol = Polygon(*polygon)
	splitLineLS = LineString(splitLine)
	extrLineLR = LinearRing(extr)


	# Check validity of the polygon
	if not pPol.is_valid:
		return []

	# This calculates the points on the boundary where the split will happen.
	commonPts = extrLineLR.intersection(splitLineLS)
	logger.debug("Cut: %10s Intersection: %10s"%(splitLineLS, commonPts))

	# No intersection check.
	if not commonPts:
		return []
	# This intersection should always have only 2 points.
	if type(commonPts) is not MultiPoint:
		return []
	# Should only ever contain two points.
	if len(commonPts) != 2:
		return []
	# Split line should be inside polygon.
	if not splitLineLS.within(pPol):
		return []
	# Check to see if cut line touches any holes
	for hole in holes:
		holeLS = LinearRing(hole)
		if splitLineLS.intersects(holeLS):
			return []




	splitBoundary = extrLineLR.difference(splitLineLS)
	# Check that splitBoundary is a collection of linestrings
	if type(splitBoundary) is not MultiLineString:
		return []
	# Make sure there are only 2 linestrings in the collection
 	if len(splitBoundary) > 3 or len(splitBoundary) < 2:
 		return []

	logger.debug("Split boundary: %s"%splitBoundary)

	# Even though we use LinearRing, there is no wrap around and diff produces
	#	3 strings. Need to union. Not sure if combining 1st and last strings 
	#	is guaranteed to be the right combo. For now, place a check.
	if len(splitBoundary) == 3:
		if splitBoundary[0].coords[0] != splitBoundary[-1].coords[-1]:
			logger.warn("The assumption that pts0[0] == pts2[-1] DOES not hold. Need"
					"to investigate. Polygon split function.")
			return []

		line1 = LineString(list(list(splitBoundary[-1].coords)[:-1]+list(splitBoundary[0].coords)))
	else:
		line1 = splitBoundary[0]
	line2 = splitBoundary[1]


	if len(line1.coords) < 3 or len(line2.coords) < 3:
		return []

	mask1 = Polygon(line1)
	mask2 = Polygon(line2)

	if (not mask1.is_valid) or (not mask2.is_valid):
		return []

	resP1Pol = pPol.intersection(mask1)
	resP2Pol = pPol.intersection(mask2)

	if type(resP1Pol) is not Polygon:
		return []
	if type(resP2Pol) is not Polygon:
		return []
	if not resP1Pol.is_valid:
		return []
	if not resP2Pol.is_valid:
		return []

	# The results of the intersection are Shapely objects. Convert them to list.
	resP1 = convert_to_canonical(resP1Pol)
	resP2 = convert_to_canonical(resP2Pol)

	return resP1, resP2


if __name__ == '__main__':


	P = [[(0, 0), (1, 0), (1, 1), (0, 1)], [[(0.1, 0.1), (0.1, 0.9), (0.9, 0.9), (0.9, 0.1)]]]
	e = [(0.05, 0), (0.05, 1)]
	P1, P2 = polygon_split(P, e)

	P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
	e = [(1, 0.8), (0.8, 1)]
	P1, P2 = polygon_split(P, e)

	P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
	e = [(0.2, 1), (0, 0.8)]
	P1, P2 = polygon_split(P, e)

	P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
	e = [(0, 0.2), (0.2, 0)]
	P1, P2 = polygon_split(P, e)
	#pretty_print_poly(P1)
	#pretty_print_poly(P2)


	# Stability test where a lot of cuts are performed on one polygon
	P = [[(0.9285714285714286, 1.785714285714285), (0.8333333333333334, 0.1666666666666667), (1.0, 0.0), (2.0, 0.0), (1.681818181818182, 1.863636363636363), (3.0, 2.0), (2.0, 3.0), (1.0, 3.0), (0.9285714285714286, 1.785714285714285)], []]
	e = [(2.711344240884324, 1.970139059401827), (1.722081099006799, 1.627810705817321)]
	
	polyExterior = Polygon(*P).exterior
	from numpy import linspace
	from itertools import product
	searchDistances = list(linspace(0, polyExterior.length, 0))

	searchSpace = []
	for distance in searchDistances:
		solutionCandidate = polyExterior.interpolate(distance)
		searchSpace.append((solutionCandidate.x, solutionCandidate.y))
	for cutEdge in product(searchSpace, repeat=2):

		result = polygon_split(P, cutEdge)

	# Stability test where a lot of cuts are performed on one polygon
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
	
	polyExterior = Polygon(*P).exterior
	from numpy import linspace
	from itertools import product
	searchDistances = list(linspace(0, polyExterior.length, 500))

	searchSpace = []
	for distance in searchDistances:
		solutionCandidate = polyExterior.interpolate(distance)
		searchSpace.append((solutionCandidate.x, solutionCandidate.y))
	successCount = 0
	for cutEdge in product(searchSpace, repeat=2):
		result = polygon_split(P, cutEdge)
		if not result:
			successCount += 1
	print successCount
