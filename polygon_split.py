from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import LineString


# Arbitrarily small epsilon for buffer operations
BUFFER_EPS = 10e-06


def polygon_split(polygon=[], split_line=[]):
	"""Split a polygon into two other polygons along split_line

	Attempts to split a polygon into two other polygons. Here, a number of
	assumptions has to be made. That is, that split_line is a proper line
	connecting 	boundaries of a polygon. Also, that split_line does not connect
	outside boundary to a boundary of hole. This is a undefined behaviour.

	Unforunately, this split is destructive due to the nature of Shapely. That
	is the two 
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
			print("Polygon split requested on an split line with wrong number of coordinates.")

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

	# Shapely doesn't support set operations between objects of different
	#	dimensionality. Hence, artificially inflate line.
	# Cap and join style are ROUND
	splitLineLS = LineString(split_line)
	splitLinePol = splitLineLS.buffer(BUFFER_EPS, cap_style=1, join_style=1)


	diff = pPol.difference(splitLinePol)

	return diff




	#print("Cut edge: %s"%(e,))
	v = e[0]
	w = e[1]
	chain = LineString(P[0]+[P[0][0]])
	#print("Chain to be cut: %s"%(chain,))
	#print("Chain length: %7f"%chain.length)

	distance_to_v = chain.project(Point(v))
	distance_to_w = chain.project(Point(w))
	if distance_to_v == 0.0 and distance_to_w == 0.0:
		return (None,None)
	if distance_to_v == distance_to_w:
		return (None,None)

	#print("D_to_w: %7f, D_to_v: %2f"%(distance_to_w, distance_to_v))

	if distance_to_w > distance_to_v:
		if round(distance_to_w, 4) >= round(chain.length, 4):
	#		print("Special case")
			distance_to_v = chain.project(Point(v))
			left_chain, right_chain = cut(chain, distance_to_v)

			p_l = left_chain.coords[:]
			if right_chain:
				p_r = right_chain.coords[:]
			else:
				p_r = []
		else:
			if distance_to_v == 0:
				distance_to_w = chain.project(Point(w))
				right_chain, remaining = cut(chain, distance_to_w)

				p_l = remaining.coords[:]
				p_r = right_chain.coords[:]	
			else:
				cut_v_1, cut_v_2 = cut(chain, distance_to_v)

				distance_to_w = cut_v_2.project(Point(w))
				right_chain, remaining = cut(cut_v_2, distance_to_w)

				p_l = cut_v_1.coords[:]+remaining.coords[:-1]
				p_r = right_chain.coords[:]

	else:
		if round(distance_to_v, 4) >= round(chain.length, 4):
	#		print("Special case")
			distance_to_w = chain.project(Point(w))
			right_chain, remaining = cut(chain, distance_to_w)

			p_l = remaining.coords[:]
			p_r = right_chain.coords[:]			
		else:
			if distance_to_w == 0:
				distance_to_v = chain.project(Point(v))
				right_chain, remaining = cut(chain, distance_to_v)

				p_l = remaining.coords[:]
				p_r = right_chain.coords[:]		
			else:
	#			print "here"
				#print chain
				cut_v_1, cut_v_2 = cut(chain, distance_to_w)
				#print("Cut1: %s"%cut_v_1)
				#print("Cut2: %s"%cut_v_2)


				distance_to_v = cut_v_2.project(Point(v))
	#			print("Dist: %2f. Length: %2f"%(distance_to_v, cut_v_2.length) )
				right_chain, remaining = cut(cut_v_2, distance_to_v)
	#			print remaining.coords[:]
				p_l = cut_v_1.coords[:]+remaining.coords[:-1]
				p_r = right_chain.coords[:]
	#			p_l = right_chain.coords[:] 
	#			p_r = remaining.coords[:]+cut_v_1.coords[:]
	#			print p_l, p_r

	return p_l, p_r


def cut(line, distance):
	"""Fetches rows from a Bigtable.

	Retrieves rows pertaining to the given keys from the Table instance
	represented by big_table.  Silly things may happen if
	other_silly_variable is not None.

	Args:
		big_table: An open Bigtable Table instance.
		keys: A sequence of strings representing the key of each table row
			to fetch.
		other_silly_variable: Another optional variable, that has a much
			longer name than the other args, and which does nothing.

	Returns:
		A dict mapping keys to the corresponding table row data
		fetched. Each row is represented as a tuple of strings. For
		example:

		{'Serak': ('Rigel VII', 'Preparer'),
		'Zim': ('Irk', 'Invader'),
		'Lrrr': ('Omicron Persei 8', 'Emperor')}

		If a key from the keys argument is missing from the dictionary,
		then that row was not found in the table.

	Raises:
		IOError: An error occurred accessing the bigtable.Table object.
	"""


	# Cuts a line in two at a distance from its starting point
	if distance <= 0.0 or distance >= line.length:
		print("ERROR: CUT BEYOND LENGTH")
		print line
		print(distance)
		return [LineString(line), []]

	coords = list(line.coords)
	#print("Coords: %s"%(coords,))
	pd = 0
	#for i, p in enumerate(coords):
	for i in range(len(coords)):
		if i > 0:
			pd = LineString(coords[:i+1]).length
		#print i,coords[:i+1]
		#pd = line.project(Point(p))
		#print pd
		if pd == distance:
			return [
				LineString(coords[:i+1]),
				LineString(coords[i:])]
		if pd > distance:
			#print("This case")
			cp = line.interpolate(distance)
			#print("cp: %s"%(cp,))
			return [
				LineString(coords[:i] + [(cp.x, cp.y)]),
				LineString([(cp.x, cp.y)] + coords[i:])]
		if i == len(coords)-1:
			cp = line.interpolate(distance)
			return [
				LineString(coords[:i] + [(cp.x, cp.y)]),
				LineString([(cp.x, cp.y)] + coords[i:])]






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

	result = polygon_split(P, e)
	if result:
		print("[PASSED] Simple polygon cut test.")
	else:
		print("[FAILED] Simple polygon cut test..")


	P = [[(0, 0), (1, 0), (1, 1), (0, 1)], [[(0.25, 0.25), (0.25, 0.75), (0.75, 0.75), (0.75, 0.25)]]]
	e = [(0, 0), (1, 1)]
	result = polygon_split(P, e)
	if result:
		print("[PASSED] Simple polygon cut test.")
	else:
		print("[FAILED] Simple polygon cut test..")

#	P1, P2 = result
#	print P1
#	print P2
