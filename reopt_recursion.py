from shapely.geometry import Polygon
from shapely.geometry import LineString

from numpy import linspace
from itertools import product

from chi import compute_chi
from polygon_split import polygon_split
from pairwise_reopt import compute_pairwise_optimal

RADIUS = 0.1
LINEAR_PENALTY = 1		# Weights for the cost function
ANGULAR_PENALTY = 10	# Weights for the cost function


def reopt_recursion_BFT(decomp=[], adj_matrix=[], v_max_id=0, cell_to_site_map=[], q=[]):
	"""
	BFT traversal
	"""
	reopt_recursion.level += 1
#	if DEBUG:
#		print("[..] Recursion level: %d"%reopt_recursion.level)
	# Compute the v_max cost
#	v_max_cost = chi.chi(polygon=decomp[v_max_id], init_pos=cell_to_site_map[v_max_id],
#						radius=RADIUS, lin_penalty=LIN_PENALTY,
#						angular_penalty=ANGULAR_PENALTY)
#	if DEBUG:
#		print("[.] Cell with maximum: %d, %f"%(v_max_id, v_max_cost))

	# Find adjacent cells to v_max
	if not q:
		return
	v_max_id = q.pop(0)

	# Compute the v_max cost
	v_max_cost = chi.chi(polygon=decomp[v_max_id], init_pos=cell_to_site_map[v_max_id],
						radius=RADIUS, lin_penalty=LINEAR_PENALTY,
						angular_penalty=ANGULAR_PENALTY)
	if DEBUG:
		print("[.] Cell with maximum: %d, %f"%(v_max_id, v_max_cost))




	neighbors = []
	for cell_id, cell in enumerate(adj_matrix[v_max_id]):
		if not cell is None:
			neighbors.append(cell_id)
	if DEBUG:
		print("[.] Neighbors: %s"%(neighbors,))

	# Comptue the cost matrix for adjacent cells
	n_chi_costs = []
	for idx in neighbors:
		cost = chi.chi(polygon=decomp[idx], init_pos=cell_to_site_map[idx],
						radius=RADIUS, lin_penalty=LINEAR_PENALTY,
						angular_penalty=ANGULAR_PENALTY)
		n_chi_costs.append((idx, cost))

	if DEBUG:
		print("[.] Neghbours and chi: %s"%n_chi_costs)

	n_chi_costs_sorted = sorted(n_chi_costs, key=lambda v:v[1], reverse=False)

	for v_i_idx, n_cost in n_chi_costs:

		if n_cost < v_max_cost:
			if DEBUG:
				print("[..] Attempting %d and %d."%(v_max_id, v_i_idx))
			#print decomp
			if pair_wise_reoptimization(v_max_id, v_i_idx, decomp, adj_matrix, cell_to_site_map):
				#mad.post_processs_decomposition(decomp)
				#adj_matrix = adj.get_adjacency_as_matrix(decomp)
				if DEBUG:
					print("[..] Cells %d and %d reopted."%(v_max_id, v_i_idx))
				return True
			else:
				# Add the neihtbouts of v_j to the queue
				if not v_i_idx in q: 
					q.append(v_i_idx)
				#if reopt_recursion(decomp, adj_matrix, v_i_idx, cell_to_site_map):
				#	break


				#mad.post_processs_decomposition(decomp)
				#adj_matrix = adj.get_adjacency_as_matrix(decomp)
	reopt_recursion_BFT(decomp, adj_matrix, v_max_id, cell_to_site_map, q)



def dft_recursion(decomposition=[],
				  adjacencyMatrix=[],
				  maxVertexIdx=0,
				  cellToSiteMap=[]):
	"""
	This is a recursive function that explores all pairs of cells starting with
	one with the highest cost. The purpose is to re-optimize cuts of adjacent
	cells such that the maximum cost over all cells in the map is minimized.

	Assumption:
		The calling function will need to initialize the level to 0

	Params:
		decomposition: A decomposition as a list of polygons.
		adjacencyMatrix: A matrix representing adjacency relationships between
						 cells in the decomposition.
        maxVertexIdx: Index of a cell in the decomposition with the maximum cost.

	"""

	dft_recursion.level += 1

	if DEBUG_LEVEL & 0x8:
		print("[..] Recursion level: %d"%reopt_recursion.level)

	maxVertexCost = compute_chi(polygon = decomposition[maxVertexIdx],
								initPos = cellToSiteMap[maxVertexIdx],
								radius = RADIUS,
								linPenalty = LINEAR_PENALTY,
								angPenalty = ANGULAR_PENALTY)
	if DEBUG_LEVEL:
		print("[.] Cell with maximum: %d, %f"%(maxVertexIdx, maxVertexCost))



	# Find adjacent cells to v_max
	neighbors = []
	for cell_id, cell in enumerate(adjacencyMatrix[maxVertexIdx]):
		if not cell is None:
			neighbors.append(cell_id)
	if DEBUG_LEVEL:
		print("[.] Neighbors: %s"%(neighbors,))


	# Comptue the cost matrix for adjacent cells
	n_chi_costs = []
	for idx in neighbors:
		cost = compute_chi(polygon = decomposition[idx],
						   initPos = cell_to_site_map[idx],
						   radius = RADIUS,
						   linPenalty = LINEAR_PENALTY,
						   angPenalty = ANGULAR_PENALTY)
		n_chi_costs.append((idx, cost))

	if DEBUG_LEVEL:
		print("[.] Neghbours and chi: %s"%n_chi_costs)

	n_chi_costs_sorted = sorted(n_chi_costs, key=lambda v:v[1], reverse=True)

	

	for v_i_idx, n_cost in n_chi_costs:

		if n_cost < maxVertexCost:
			if DEBUG_LEVEL:
				print("[..] Attempting %d and %d."%(v_max_id, v_i_idx))
			#print decomp


			# NEED TO CHANGE A LOT OF THINGS HERER
			if compute_pairwise_optimal(v_max_id, v_i_idx, decomp, adj_matrix, cell_to_site_map):
				#mad.post_processs_decomposition(decomp)
				#adj_matrix = adj.get_adjacency_as_matrix(decomp)
				if DEBUG:
					print("[..] Cells %d and %d reopted."%(v_max_id, v_i_idx))
				return True
			else:
				if reopt_recursion(decomp, adj_matrix, v_i_idx, cell_to_site_map):
					break
	return False

				#mad.post_processs_decomposition(decomp)
				#adj_matrix = adj.get_adjacency_as_matrix(decomp)

if __name__ == '__main__':

	# If package is launched from cmd line, run sanity checks
	global DEBUG_LEVEL

	DEBUG_LEVEL = 0 #0x8+0x4

	print("\nSanity tests for recursive reoptimization.\n")


	P = [[(0.0,0.0),(10.0,0.0),(10.0,1.0),(0.0,1.0)],[]]
	q = [(0.0,0.0),(10.0,0.0),(10.0,1.0),(0.0,1.0)]
	decomposition = [[[(0.0,0.0),(2.5,0.0),(2.5,1.0),(0.0,1.0)],[]], [[(2.5,0.0),(5.0,0.0),(5.0,1.0),(2.5,1.0)],[]], [[(5.0,0.0),(7.5,0.0),(7.5,1.0),(5.0,1.0)],[]], [[(7.5,0.0),(10.0,0.0),(10.0,1.0),(7.5,1.0)],[]]]
	adjMatrix = [[None, [(2.5,0.0),(2.5,1.0)], None, None], [(2.5,0.0),(2.5,1.0), None, [(5.0,0.0),(5.0,1.0)], None], [None, [(5.0,0.0),(5.0,1.0)], None, [(7.5,1.0), (7.5,0.0)]], [None, None, [(7.5,1.0), (7.5,0.0)], None]]
	cell_to_site_map = {0: (10,0), 1:(10,1), 2:(0,1), 3:(0,0)}
	dft_recursion.level = 0
	dft_recursion(decomposition, adjMatrix, 3, cell_to_site_map)
	#result = "PASS" if not dft_recursion(P1, P2, initA, initB) else "FAIL"
	#print("[%s] Simple two polygon test."%result)