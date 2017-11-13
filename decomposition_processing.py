from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import Point


def collinear_correction(decomp):

	for poly in decomp:
		boundary = poly[0]
		i = 0
		while i < len(boundary):
			p1 = boundary[i]
			p2 = boundary[(i+1)%len(boundary)]
			p3 = boundary[(i+2)%len(boundary)]
			if cuts.collinear(p1, p2, p3):
				del boundary[(i+1)%len(boundary)]
			i += 1

def compute_adjacency(decomposition=[]):
	"""
	Computes an adjacency relation for the polygons in the decomposition.
	In the effect, computes a graph where the nodes are polygons and the edges
	represent adjacency between polygons.

	Assumption:
		The polygons are considered adjacent if their boundaries intersect at an
		edge. If they only touch at a point, then will not be considered
		adjacent.

	Params:
		decomposition: A list of polygons in the canonical form.

	Returns:
		A 2D list representing adjacency relation between polygons.
	"""

	# Initialize the 2D matric with None values.
	adjMatrix = [[False for i in range(len(decomposition))] for i in range(len(decomposition))]

	for polyAIdx in range(len(decomposition)):
		for polyBIdx in range(polyAIdx + 1, len(decomposition)):

			try:
				polyAShapely = Polygon(*decomposition[polyAIdx])
				polyBShapely = Polygon(*decomposition[polyBIdx])
			except:
				print("Computing adjacency but decomposition contains invalid polygons")
				return []

			if not polyAShapely.touches(polyBShapely):
				continue

			intersection = polyAShapely.intersection(polyBShapely)

			if type(intersection) is Point:
				continue
			else:
				adjMatrix[polyAIdx][polyBIdx] = True
				adjMatrix[polyBIdx][polyAIdx] = True

	return adjMatrix


if __name__ == '__main__':

	# If package is launched from cmd line, run sanity checks
	global DEBUG_LEVEL

	DEBUG_LEVEL = 0 #0x8+0x4

	print("\nSanity tests for pairwise reoptimization.\n")

	polySet = [[[(0, 0), (1, 0), (1, 1), (0, 1)], []],
			   [[(1, 0), (2, 0), (2, 1), (1, 1)], []],
			   [[(1, 1), (2, 1), (2, 2), (1, 2)], []],
			   [[(0, 1), (1, 1), (1, 2), (0, 2)], []]]
	print(compute_adjacency(polySet))

	polySet = [[[(0, 0), (1, 0), (1, 1), (0.5, 0.5), (0, 1)], []],
			   [[(1, 0), (2, 0), (2, 1), (1, 1)], []],
			   [[(1, 1), (2, 1), (2, 2), (1, 2)], []],
			   [[(0, 1), (0.5, 0.5), (1, 1), (1, 2), (0, 2)], []]]
	print(compute_adjacency(polySet))