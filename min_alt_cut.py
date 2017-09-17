from math import atan2
from math import pi
from itertools import product

from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import LineString

from rotation import rotate_points
from polygon_split import polygon_split
from altitude import get_altitude


def compute_transition_point(edge=[], theta=0, cutVertex=[]):
	"""Computes the transition point for a given theta and cutVertex

	This function computes transition point as defined in the paper. If
	there is no transition point, returns []

	Args:
		edge: A straight line segment representing an edge for a cut
		theta: Orientation for which the transition point is required in rad
		cutVertex: Vertex of origin of cone of bisection
	Returns:
		transitionPt: A transition point or [] if no pt exists
	"""


	if not edge:
		if DEBUG_LEVEL & 0x04:
			print("Transition point compute is requested in empty input.")
		return []

	if not cutVertex:
		if DEBUG_LEVEL & 0x04:
			print("Transition point compute is requested in empty input.")
		return []


	rotatedEdge = rotate_points(edge, -1.0*theta)
	rotatedCutOrigin = rotate_points([cutVertex], -theta)[0]

	minYidx, (tmpX, minY) = min(enumerate(rotatedEdge), key=lambda pt: pt[1][1])
	maxYidx, (tmpX, maxY) = max(enumerate(rotatedEdge), key=lambda pt: pt[1][1])

	minXidx, (minX, tmpY) = min(enumerate(rotatedEdge), key=lambda pt: pt[1][0])
	maxXidx, (maxX, tmpY) = max(enumerate(rotatedEdge), key=lambda pt: pt[1][0])

	if minX < rotatedCutOrigin[0] and rotatedCutOrigin[0] < maxX:

		line = LineString([(rotatedCutOrigin[0], maxY+1),
						   (rotatedCutOrigin[0], minY-1)])
		transitionPt = LineString(rotatedEdge).intersection(line)

		if Point(rotatedCutOrigin).intersects(LineString(rotatedEdge)):
			if DEBUG_LEVEL & 0x04:
				print("Transition pt requested but vrt is in the edge")

			return []

		if not transitionPt or type(transitionPt) is not Point:

			if DEBUG_LEVEL & 0x04:
				print("Transition pt requested but intesection was not valid")

			return []

		if DEBUG_LEVEL & 0x8:
			print("Intersection line: %s "%(line,))
			print("Edge: %s"%(rotatedEdge,))
			print("Transition Point: %s"%(transitionPt,))

		return rotate_points([transitionPt.coords[0]], theta)[0]

	else:

		if DEBUG_LEVEL & 0x8:
			print("minX: %d maxX: %d "%(minX, maxX))
			print("rotatedVrt: %s"%(rotatedCutOrigin,))

		return []
		

def get_directions_set(polygon=[]):
	"""Generates a list of directions orthogonal to edges of polygon

	[TODO]: Efficiency could be improved by removing duplicate directions

	Augs:
		polygon: a polygon in standard form
	Returns:
		directions: set of directions [rad]
	"""

	ext = P[0]
	holes = P[1]
	directions = []

	n = len(ext)
	for i in range(n):
		ax, ay = ext[i]
		bx, by = ext[(i+1)%n]

		directions.append(atan2(by-ay, bx-ax)+pi/2)


	for hole in holes:
		n = len(hole)
		for i in range(n):
			edge = [hole[i], hole[(i+1)%n]]
			ax, ay = edge[0]
			bx, by = edge[1]

			directions.append(atan2(by-ay, bx-ax)+pi/2)

	return directions


def compute_min_alt_cut(polygon=[], vrtx=[]):
	"""Computes minimum altitude cut in a polygon from a refelx vertex.

	For a given polygon and a vertex, the function computes a cut that results
	in a pair of polygons and a minimum overall altitude.

	Several implementations of this function:
		1) Uses cones of bisection and visibility polygons to narrow down the
			search space of cuts.
		2) Uses all edges of the polygon as a search space for cuts.

	Assumptions:
		vrtx is taken from the list of verticies in the polygon chains.
			Otherwise, we may not find on the chain properly.

	Here, we will implement the second approach for improved robustness.
	Could result in excessive computation time.

	Args:
		polygon: Polygon in the form of [ [], [[],...] ] where polygon[0] is
			the exterior boundary of the polygon and polygon[1] is the list
			of boundaries of holes.
			Exterior boundary must be in ccw order. Last point != first point.
			Same for hole boundaries.
		vrtx: A vertex from which the cut is made. Can be reflex or not.

	Returns:
		minimum cut pair: List of following format:
			[TODO:] Not sure yet.
	"""


	if not polygon:
		if DEBUG_LEVEL & 0x04:
			print("Min alt cut is requested on an empty polygon.")
		return []

	if len(polygon[0]) < 3:
		if DEBUG_LEVEL & 0x04:
			print("Min alt cut is requested on a line.")
		return []


	if not vrtx:
		if DEBUG_LEVEL & 0x04:
			print("Min alt cut is requested with empty vertex.")
		return []

	if not Polygon(*polygon).is_simple:
		if DEBUG_LEVEL & 0x04:
			print("Min cut is requested on an non simple polygon.")
		return []		

	if not Polygon(*polygon).is_valid:
		if DEBUG_LEVEL & 0x04:
			print("Min cut is requested on an non valid polygon.")
		return []	

	# Generate a list of directions for the polygon
	directions = get_directions_set(polygon)
	
	# Find the minimum altitude for original polygon, a.k.a no cut
	minDirection = min(directions, key=lambda theta: get_altitude(P, theta))
	minAltitudeOriginal = get_altitude(polygon, minDirection)


	# Initialize and compute a list containing candidates for the optimal cut.
	# Due to the nature of floats, this list will contain a lot of duplicates.
	# [TODO]: Get rid of duplicates
	cutCandidates = []

	ext, holes = P

	n = len(ext)
	for i in range(n):
		edge = [ext[i], ext[(i+1)%n]]

		cutCandidates.append(ext[i])

		# Iterate over all directions and find transition points
		for theta in directions:
			transPt = compute_transition_point(edge, theta, vrtx)
			if transPt:
				cutCandidates.append(transPt)

		if DEBUG_LEVEL & 0x8:
			print("Cut end points candidates so far: %s"%cutCandidates)


	# For any pair of directions, cut and evaluate
	minCost = 10e10
	minCandidate = []

	for dirPair in product(directions, repeat=2):
		for cutCand in cutCandidates:

			splitLine = ([vrtx, cutCand])
			result = polygon_split(P, splitLine)

			if DEBUG_LEVEL % 0x8:
				if result:
					print("%s Split Line: %s"%('GOOD', splitLine,))
				else:
					print("%s Split Line: %s"%("BAD ", splitLine))

			if result:
				pol1, pol2 = result

				alt1 = get_altitude(pol1, dirPair[0])
				alt2 = get_altitude(pol2, dirPair[1])

				totalAlt = alt1+alt2

				if totalAlt <= minCost:
					minCandidate = (cutCand, dirPair)
					minCost = totalAlt

	if DEBUG_LEVEL & 0x8:
		print("Computed minimum altitude as: %4.2f"%minCost)
		print("Cut: %s"%[vrtx, minCandidate[0]])
		print("Direction 1: %4.2f Direc tion 2: %4.2f"%(minCandidate[1][0], minCandidate[1][1]))

	if minAltitudeOriginal < minCost:
		if DEBUG_LEVEL & 0x8:
			print("No cut results in minimum altitude")
	
		return []

	return minCandidate

if __name__ == '__main__':

	# If package is launched from cmd line, run sanity checks
	global DEBUG_LEVEL

	DEBUG_LEVEL = 0 #0x8+0x4

	print("Sanity tests for transition point computation.")

	result = "PASS" if not compute_transition_point([], 0, (1, 0)) else "FAIL"
	print("[%s] Empty E test."%result)

	result = "PASS" if not compute_transition_point([], 0, []) else "FAIL"
	print("[%s] Empty V test."%result)

	e = [(0, 1), (0.1, 1)]
	result = "PASS" if not compute_transition_point(e, 0, (1, 0)) else "FAIL"
	print("[%s] No intersection test."%result)

	e = [(2, 1), (2.1, 1)]
	result = "PASS" if not compute_transition_point(e, 0, (1, 0)) else "FAIL"
	print("[%s] No intersection test."%result)

	e = [(2, 1), (2.1, 1)]
	result = "PASS" if not compute_transition_point(e, 0, (2, 1)) else "FAIL"
	print("[%s] Overlapping point test."%result)	

	e = [(0, 1), (0.1, 1)]
	result = "PASS" if not compute_transition_point(e, 3/2, (1, 0)) else "FAIL"
	print("[%s] No intersection test."%result)

	e = [(1, 1), (1, 2)]
	result = "PASS" if not compute_transition_point(e, 0, (1, 0)) else "FAIL"
	print("[%s] Vertical intersection test."%result)

	e = [(0, 1), (2, 1)]
	transPt = compute_transition_point(e, 0, (1, 0))
	result = "PASS"
	if transPt != (1, 1):
		result = "FAIL"
	print("[%s] Normal intersection test."%result)

	e = [(-1, 2), (-1, 0)]
	transPt = compute_transition_point(e, pi/2, (0, 0))
	result = "PASS"
	if (round(transPt[0]), round(transPt[1])) != (-1, 0):
		result = "FAIL"
	print("[%s] Rotated normal intersection test."%result)

	e = [(-1, 2), (-1, 0)]
	transPt = compute_transition_point(e, pi/2, (0, 0))
	result = "PASS"
	if (round(transPt[0]), round(transPt[1])) != (-1, 0):
		result = "FAIL"
	print("[%s] Rotated normal intersection test."%result)



	print("\n\nSanity test for the min alt computation procedure.")

	P = [[(0, 0), (1, 0), (1.5, 1), (2, 0), (3, 0), (3, 2), (0, 2)], []]
	minCut = compute_min_alt_cut(P, (1.5, 1))
	result = "FAIL"
	if minCut == ((1.5, 2.0), (0.0, 0.0)):
		result = "PASS"
	print("[%s] Simple shape cut test."%result)

	P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
	minCut = compute_min_alt_cut(P, (0, 0))
	result = "FAIL"
	if not minCut:
		result = "PASS"
	print("[%s] Simple shape cut test."%result)

	P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
	minCut = compute_min_alt_cut(P, (-1, 0))
	result = "FAIL"
	if not minCut:
		result = "PASS"
	print("[%s] Origin outside the polygon test."%result)

	P = [[(0, 0), (-1,0), (1, 0), (1, 1), (0, 1)], []]
	minCut = compute_min_alt_cut(P, (0, 0))
	result = "FAIL"
	if not minCut:
		result = "PASS"
	print("[%s] Self-intersecting polygon test."%result)

	P = [[(0, 0), (-1,0)], []]
	minCut = compute_min_alt_cut(P, (0, 0))
	result = "FAIL"
	if not minCut:
		result = "PASS"
	print("[%s] No polygon but line test."%result)
