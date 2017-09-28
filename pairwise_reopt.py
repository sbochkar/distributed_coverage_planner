from shapely.geometry import Polygon
from shapely.geometry import LineString

from numpy import linspace
from itertools import product

from chi import compute_chi
from polygon_split import polygon_split


RADIUS = 0.1
LINEAR_PENALTY = 1		# Weights for the cost function
ANGULAR_PENALTY = 10	# Weights for the cost function

DEBUG_LEVEL = 0


def poly_shapely_to_canonical(polygon=[]):
	"""
	A simple helper function to convert a shapely object representing a polygon
	intop a cononical form polygon.

	Args:
		polygon: A shapely object representing a polygon

	Returns:
		A polygon in canonical form.
	"""

	if not polygon:
		return []

	canonicalPolygon = []
	
	if polygon.exterior.is_ccw:
		polyExterior = list(polygon.exterior.coords)
	else:
		polyExterior = list(polygon.exterior.coords)[::-1]


	holes = []
	for hole in polygon.interiors:
		if hole.is_ccw:
			holes.append(list(polygon.exterior.coords)[::-1])
		else:
			holes.append(list(polygon.exterior.coords))

	canonicalPolygon.append(polyExterior)
	canonicalPolygon.append(holes)

	return canonicalPolygon


def compute_pairwise_optimal(polygonA=[],
							 polygonB=[],
							 robotAInitPos=[],
							 robotBInitPos=[],
							 nrOfSamples=100):
	"""
	Takes two adjacent polygons and attempts to modify the shared edge such that
	the metric chi is reduced.

	TODO:
		Need to investigate assignment of cells to robots.

	Args:
		polygonA: First polygon in canonical form.
		polygonB: Second polygoni n canonical form.
		robotAInitPos: Location of robot A.
		robotBInitPos: Location of robot B.
		nrOfSamples: Samppling density to be used in the search for optimal cut.

	Returns:
		Returns the cut that minimizes the maximum chi metrix. Or [] if no such
		cut exists or original cut is the best.
	
	"""

	# The actual algorithm:
	# 1) Combine the two polygons
	# 2) Find one cut that works better
	# 3) Return that cut or no cut if nothing better was found

	if not polygonA or not polygonB:
		if DEBUG_LEVEL & 0x04:
			print("Pairwise reoptimization is requested on an empty polygon.")
		return []

	if not robotAInitPos or not robotBInitPos:
		if DEBUG_LEVEL & 0x04:
			print("Pairwise reoptimization is requested on an empty init pos.")
		return []

	if not Polygon(*polygonA).is_valid or not Polygon(*polygonB).is_valid:
		if DEBUG_LEVEL & 0x04:
			print("Pariwise reoptimization is requested on invalid polygons.")
		return []

	if not Polygon(*polygonA).is_valid or not Polygon(*polygonB).is_valid:
		if DEBUG_LEVEL & 0x04:
			print("Pariwise reoptimization is requested on invalid polygons.")
		return []

	if not Polygon(*polygonA).is_simple or not Polygon(*polygonB).is_simple:
		if DEBUG_LEVEL & 0x04:
			print("Pariwise reoptimization is requested on nonsimple polygons.")
		return []

	if not Polygon(*polygonA).touches(Polygon(*polygonB)):
		if DEBUG_LEVEL & 0x04:
			print("Pariwise reoptimization is requested on nontouching polys.")
		return []


	# Check that the polygons intersect only at the boundary and one edge
	intersection = Polygon(*polygonA).intersection(Polygon(*polygonB))


	if type(intersection) is not LineString:
		if DEBUG_LEVEL & 0x04:
			print("Pariwise reoptimization is requested but they don't touch\
				   at an edge.")
		return []


	# Combine the two polygons
	polygonUnion = Polygon(*polygonA).union(Polygon(*polygonB))
    
    # Also create a copy of polygonUnion in canonical form
	polygonUnionCanon = poly_shapely_to_canonical(polygonUnion)

	if not polygonUnion.is_valid or not polygonUnion.is_simple:
		if DEBUG_LEVEL & 0x04:
			print("Pariwise reoptimization is requested but the union resulted\
				   in bad polygon.")
		return []

	if type(polygonUnion) is not Polygon:
		if DEBUG_LEVEL & 0x04:
			print("Pariwise reoptimization is requested but union resulted in\
				   non polygon.")
		return []



	# Perform intialization stage for the optimization
	# Initializae the search space as well original cost
	polyExterior = polygonUnion.exterior
	searchDistances = list(linspace(0, polyExterior.length, nrOfSamples))

	searchSpace = []
	for distance in searchDistances:
		solutionCandidate = polyExterior.interpolate(distance)
		searchSpace.append((solutionCandidate.x, solutionCandidate.y))


	# Record the costs at this point
	chiL = compute_chi(polygon = polygonA,
						initPos = robotAInitPos,
						radius = RADIUS,
						linPenalty = LINEAR_PENALTY,
						angPenalty = ANGULAR_PENALTY)
	chiR = compute_chi(polygon = polygonB,
						initPos = robotBInitPos,
						radius = RADIUS,
						linPenalty = LINEAR_PENALTY,
						angPenalty = ANGULAR_PENALTY)

	initMaxChi = max(chiL, chiR)

	minMaxChi = 10e10
	minCandidate = []

	# This search is over any two pairs of samples points on the exterior
	# It is a very costly search.
	for cutEdge in product(searchSpace, repeat=2):

		if DEBUG_LEVEL & 0x8:
			print("polygonUnionCanon: %s"%polygonUnionCanon)
			print("Cut candidate: %s"%(cutEdge, ))
		
		result = polygon_split(polygonUnionCanon, cutEdge)

		if DEBUG_LEVEL & 0x8:
			if result:
				print("%s Split Line: %s"%('GOOD', cutEdge,))
			else:
				print("%s Split Line: %s"%("BAD ", cutEdge))

		if result:
			chiL = compute_chi(polygon = result[0],
								initPos = robotAInitPos,
								radius = RADIUS,
								linPenalty = LINEAR_PENALTY,
								angPenalty = ANGULAR_PENALTY)
			chiR = compute_chi(polygon = result[1],
								initPos = robotBInitPos,
								radius = RADIUS,
								linPenalty = LINEAR_PENALTY,
								angPenalty = ANGULAR_PENALTY)

			maxChi = max(chiL, chiR)
			if maxChi <= minMaxChi:
				minCandidate = cutEdge
				minMaxChi = maxChi

	if DEBUG_LEVEL & 0x8:
		print("Computed min max chi as: %4.2f"%minMaxChi)
		print("Cut: %s"%(minCandidate, ))

	if initMaxChi < minMaxChi:
		if DEBUG_LEVEL & 0x8:
			print("No cut results in minimum altitude")
	
		return []

	newPolygons = polygon_split(polygonUnionCanon, minCandidate)
	return newPolygons


if __name__ == '__main__':

	# If package is launched from cmd line, run sanity checks
	global DEBUG_LEVEL

	DEBUG_LEVEL = 0 #0x8+0x4

	print("\nSanity tests for pairwise reoptimization.\n")


	P1 = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
	P2 = [[(1, 0), (2, 0), (2, 1), (1, 1)], []]
	initA = (0, 0)
	initB = (1, 0)
	result = "PASS" if not compute_pairwise_optimal(P1, P2, initA, initB) else "FAIL"
	print("[%s] Simple two polygon test."%result)

	P1 = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
	P2 = [[(1, 0), (2, 0), (2, 1), (1, 1)], []]
	initA = (0, 0)
	initB = (0, 0)
	print compute_pairwise_optimal(P1, P2, initA, initB)

	P1 = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
	P2 = [[(1, 0), (2, 0), (2, 1), (1, 1)], []]
	initA = (0, 0)
	initB = (0, 1)
	print compute_pairwise_optimal(P1, P2, initA, initB)	
