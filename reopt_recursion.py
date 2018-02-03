from shapely.geometry import Polygon
from shapely.geometry import LineString

from numpy import linspace
from itertools import product

from chi import compute_chi
from pairwise_reopt import compute_pairwise_optimal
from decomposition_processing import compute_adjacency

# Need to move these to the main calling function
RADIUS = 0.2
LINEAR_PENALTY = 1.0
ANGULAR_PENALTY = 10*1.0/360
DEBUG_LEVEL = 0

def dft_recursion(decomposition=[],
				  adjacencyMatrix=[],
				  maxVertexIdx=0,
				  cellToSiteMap=[],
				  radius = 0.1,
				  linPenalty = 1.0,
				  angPenalty = 10*1.0/360):
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

	maxVertexCost = compute_chi(polygon = decomposition[maxVertexIdx],
								initPos = cellToSiteMap[maxVertexIdx],
								radius = radius,
								linPenalty = linPenalty,
								angPenalty = angPenalty)

	if DEBUG_LEVEL & 0x8:
		print("Cell %d has maximum cost of : %f"%(maxVertexIdx, maxVertexCost))


	surroundingCellIdxs = []
	for cellIdx, isAdjacent in enumerate(adjacencyMatrix[maxVertexIdx]):
		if isAdjacent:
			surroundingCellIdxs.append(cellIdx)

	if DEBUG_LEVEL & 0x8:
		print("Surrounding Cell Idxs: %s"%(surroundingCellIdxs,))


	surroundingChiCosts = []
	for cellIdx in surroundingCellIdxs:
		cost = compute_chi(polygon = decomposition[cellIdx],
						   initPos = cellToSiteMap[cellIdx],
						   radius = radius,
						   linPenalty = linPenalty,
						   angPenalty = angPenalty)
		surroundingChiCosts.append((cellIdx, cost))


	sortedSurroundingChiCosts = sorted(surroundingChiCosts,
									   key = lambda v:v[1],
									   reverse = False)
	if DEBUG_LEVEL & 0x8:
		print("Neghbours and chi: %s"%sortedSurroundingChiCosts)

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
				print("Attempting reopt %d and %d."%(maxVertexIdx, cellIdx))


			result = compute_pairwise_optimal(polygonA = decomposition[maxVertexIdx],
											  polygonB = decomposition[cellIdx],
											  robotAInitPos = cellToSiteMap[maxVertexIdx],
											  robotBInitPos = cellToSiteMap[cellIdx],
											  nrOfSamples = 100,
											  radius = radius,
											  linPenalty = linPenalty,
											  angPenalty = angPenalty)

			if result:
				# Resolve cell-robot assignments here.
				# This is to avoid the issue of cell assignments that
				# don't make any sense after polygon cut.
				chiA0 = compute_chi(polygon = result[0],
								   	initPos = cellToSiteMap[maxVertexIdx],
								   	radius = radius,
								   	linPenalty = linPenalty,
								   	angPenalty = angPenalty)
				chiA1 = compute_chi(polygon = result[1],
								   	initPos = cellToSiteMap[maxVertexIdx],
								   	radius = radius,
								   	linPenalty = linPenalty,
								   	angPenalty = angPenalty)
				chiB0 = compute_chi(polygon = result[0],
								   	initPos = cellToSiteMap[cellIdx],
								   	radius = radius,
								   	linPenalty = linPenalty,
								   	angPenalty = angPenalty)							   	
				chiB1 = compute_chi(polygon = result[1],
								   	initPos = cellToSiteMap[cellIdx],
								   	radius = radius,
								   	linPenalty = linPenalty,
								   	angPenalty = angPenalty)

				if max(chiA0, chiB1) <= max(chiA1, chiB0):
					decomposition[maxVertexIdx], decomposition[cellIdx] = result
				else:
					decomposition[cellIdx], decomposition[maxVertexIdx] = result

				if DEBUG_LEVEL & 0x8:
					print("Cells %d and %d reopted."%(maxVertexIdx, cellIdx))

				adjacencyMatrix = compute_adjacency(decomposition)
				
				return True
			else:
				if dft_recursion(decomposition = decomposition,
								 adjacencyMatrix = adjacencyMatrix,
								 maxVertexIdx = cellIdx,
								 cellToSiteMap = cellToSiteMap,
								 radius = radius,
								 linPenalty = linPenalty,
								 angPenalty = angPenalty):
					return True
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