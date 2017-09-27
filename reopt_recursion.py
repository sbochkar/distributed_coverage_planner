from shapely.geometry import Polygon
from shapely.geometry import LineString

from numpy import linspace
from itertools import product

from chi import compute_chi
from pairwise_reopt import compute_pairwise_optimal
from decomposition_processing import compute_adjacency

RADIUS = 0.1
LINEAR_PENALTY = 1		# Weights for the cost function
ANGULAR_PENALTY = 10	# Weights for the cost function


def dft_recursion(decomposition=[],
				  adjacencyMatrix=[],
				  maxVertexIdx=0,
				  cellToSiteMap=[]):
	"""
	This is a recursive function that explores all pairs of cells starting with
	one with the highest cost. The purpose is to re-optimize cuts of adjacent
	cells such that the maximum cost over all cells in the map is minimized.

	Assumption:
		The adjacency value for a cell with iteself should be None

	Params:
		decomposition: A decomposition as a list of polygons.
		adjacencyMatrix: A matrix representing adjacency relationships between
						 cells in the decomposition.
		maxVertexIdx: Index of a cell in the decomposition with the maximum cost.

	Returns:
		True if a succseful reoptimization was performed. False otherwise.
	"""

	if DEBUG_LEVEL & 0x8:
		print("Recursion level: %d"%reopt_recursion.level)
		print("Cell %d has maximum cost of : %f"%(maxVertexIdx, maxVertexCost))

	maxVertexCost = compute_chi(polygon = decomposition[maxVertexIdx],
								initPos = cellToSiteMap[maxVertexIdx],
								radius = RADIUS,
								linPenalty = LINEAR_PENALTY,
								angPenalty = ANGULAR_PENALTY)

	if DEBUG_LEVEL & 0x8:
		print("Cell %d has maximum cost of : %f"%(maxVertexIdx, maxVertexCost))


	surroundingCellIdxs = []
	for cellIdx, cell in enumerate(adjacencyMatrix[maxVertexIdx]):
		if cell is not None:
			surroundingCellIdxs.append(cellIdx)

	if DEBUG_LEVEL & 0x8:
		print("[.] Surrounding Cell Idxs: %s"%(surroundingCellIdxs,))


	surroundingChiCosts = []
	for cellIdx in surroundingCellIdxs:
		cost = compute_chi(polygon = decomposition[cellIdx],
						   initPos = cellToSiteMap[cellIdx],
						   radius = RADIUS,
						   linPenalty = LINEAR_PENALTY,
						   angPenalty = ANGULAR_PENALTY)
		surroundingChiCosts.append((cellIdx, cost))

	if DEBUG_LEVEL & 0x8:
		print("Neghbours and chi: %s"%surroundingChiCosts)

	sortedSurroundingChiCosts = sorted(surroundingChiCosts,
									   key = lambda v:v[1],
									   reverse = False)

	# Idea: For a given cell with maximum cost, search all the neighbors
	#		and sort them based on their chi cost.
	#
	#		Starting with the neighbor with the lowest cost, attempt to
	#		reoptimize the cut seperating them in hopes of minimizing the max
	#		chi of the two cells.
	#
	#		If the reoptimization was succesful then stop recursion and complete
	#		the iteration.
	#
	#		If the reoptimization was not succesful then it is possible that we
	#		are in a local minimum and we need to disturb the search in hopes
	#		of finiding a better solution.
	#
	#		For that purpose, we call the recursive function on the that
	#		neighboring cell. And so on.
	#
	#		If the recursive function for that neighboring cell does not yield
	#		a reoptimization then we pick the next lowest neighbor and attempt
	#		recursive reoptimization. This ensures DFT of the adjacency graph.

	for cellIdx, cellChiCost in sortedSurroundingChiCosts:

		if cellChiCost < maxVertexCost:
			if DEBUG_LEVEL & 0x8:
				print("Attempting %d and %d."%(maxVertexIdx, cellIdx))


			result = compute_pairwise_optimal(polygonA = decomposition[maxVertexIdx],
											  polygonB = decomposition[cellIdx],
											  robotAInitPos = cellToSiteMap[maxVertexIdx],
											  robotBInitPos = cellToSiteMap[cellIdx],
											  nrOfSamples = 100)

			if result:
				decomposition[maxVertexIdx], decomposition[cellIdx] = result

				if DEBUG_LEVEL & 0x8:
					print("Cells %d and %d reopted."%(maxVertexIdx, cellIdx))

				adjacencyMatrix = compute_adjacency(decomposition)
				
				return True
			else:
				if dft_recursion(decomposition = decomposition,
								 adjacencyMatrix = adjacencyMatrix,
								 maxVertexIdx = cellIdx,
								 cellToSiteMap = cellToSiteMap):
					break
	return False


if __name__ == '__main__':

	# If package is launched from cmd line, run sanity checks
	global DEBUG_LEVEL

	DEBUG_LEVEL = 0 #0x8+0x4

	print("\nSanity tests for recursive reoptimization.\n")


	P = [[(0.0,0.0),(10.0,0.0),(10.0,1.0),(0.0,1.0)],[]]
	q = [(0.0,0.0),(10.0,0.0),(10.0,1.0),(0.0,1.0)]
	decomposition = [[[(0.0,0.0),(2.5,0.0),(2.5,1.0),(0.0,1.0)],[]], [[(2.5,0.0),(5.0,0.0),(5.0,1.0),(2.5,1.0)],[]], [[(5.0,0.0),(7.5,0.0),(7.5,1.0),(5.0,1.0)],[]], [[(7.5,0.0),(10.0,0.0),(10.0,1.0),(7.5,1.0)],[]]]
	adjMatrix = [[False, True, False, False], [True, False, True, False], [False, True, False, True], [False, False, True, False]]
	cell_to_site_map = {0: (10,0), 1:(10,1), 2:(0,1), 3:(0,0)}
	print dft_recursion(decomposition, adjMatrix, 3, cell_to_site_map)
	print decomposition
	#result = "PASS" if not dft_recursion(P1, P2, initA, initB) else "FAIL"
	#print("[%s] Simple two polygon test."%result)