from math import atan2
from math import pi

from shapely.geometry import Point
from shapely.geometry import LineString

from rotation import rotate_points


def compute_transition_point(edge=[], theta=[], cutVertex=[]):
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


	rotatedEdge = rotate_points(edge, -theta)
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

		dirs.append(atan2(by-ay, bx-ax)+pi/2)


	for hole in holes:
		n = len(hole)
		for i in range(n):
			edge = [hole[i], hole[(i+1)%n]]
			ax, ay = edge[0]
			bx, by = edge[1]

			dirs.append(atan2(by-ay, bx-ax)+pi/2)

	return dirs


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
		[TODO:] Not sure yet.
	"""


	if not polygon:
		return []

	if not vrtx:
		return []


	# Generate a list of directions for the polygon
	directions = get_directions_set(polygon)

	# Initialize and compute a list containing candidates for the optimal cut.
	cutCandidates = []

	ext, holes = P

	n = len(ext)
	for i in range(n):
		edge = [ext[i], ext[(i+1)%n]]

		directions.append(ext[i])

		# Iterate over all directions and find transition points
		for theta in directions:
			transPt = compute_transition_point(edge, theta, rtx)
			if transPt:
				directions.append(transPt)


	# Evaluate these candidates



	# 1 Initialize a list of candidate cut points
	# 2 Generate a list of directions
	# For each edge of a polygon
	# 3 Add edge endpoints to the list of candidates
	# 4 Calculate transition points foreach direction and add to the cand list

	# 5 Continue with evaluation







	# First order of business, set up data structures to assist in computation.
	# Shift the exterior boundary of the polygon such that the vrtx is the first
	#	vertex.
	try:
		vrtxIdx = polygon[0].index(vrtx)
	except:
		return []

	extr = list(polygon[0][vrtxIdx:]) + list(polygon[0][:vrtxIdx])



	for si in s:
		# Process each edge si, have to be cw
		lr_si = LinearRing([v[1]]+si)
		if lr_si.is_ccw:
			#print lr_si
			#print lr_si.is_ccw
			si = [si[1]]+[si[0]]
			#print si


		cut_point = si[0]
		#print P, v, cut_point
		result = polygon_split.split_polygon(P, [v[1], cut_point])
		if not result:
			continue

		p_r, p_l = result
		if not LineString(p_l).is_simple:
			continue
		if not LineString(p_r).is_simple:
			continue

		dirs_left = directions.get_directions_set([p_l, []])
		dirs_right = directions.get_directions_set([p_r, []])

		#print dirs_left
		#print list(degrees(dir) for dir in dirs_left)
		#print get_altitude([p_l,[]], 3.5598169831690223)
		#print get_altitude([p_r,[]], 0)

		# Look for all transition points
		for dir1 in dirs_left:
			for dir2 in dirs_right:
				tp = find_best_transition_point(si, v[1], dir1, dir2)
				# Here check if tp is collinear with v
				# If so and invisible, replace with visible collinear point
				if tp in collinear_dict.keys():
					pois.append((collinear_dict[tp], dir1, dir2))
				else:
					pois.append((tp, dir1, dir2))






if __name__ == '__main__':

	# If package is launched from cmd line, run sanity checks
	DEBUG_LEVEL = 0 # 0x8+0x4

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





	P = [[(0, 0), (1, 0), (1, 1), (0, 1)], []]
	e = [(0, 0), (1, 1)]

	compute_min_alt_cut(P, (0, 0))
	compute_min_alt_cut(P, (1, 0))
	compute_min_alt_cut(P, (1, 1))
	compute_min_alt_cut(P, (0, 1))