from decomposition_processing import compute_adjacency
from chi import compute_chi
from reopt_recursion import dft_recursion


DEBUG_LEVEL = 0x2

def chi_reoptimize(decomposition = [],
				   cellToSiteMap = [],
				   originalChiCosts = [],
				   newChiCosts = [],
				   numIterations = 10,
				   radius = 0.1,
				   linPenalty = 1.0,
				   angPenalty = 10*1.0/360):
	"""
	Performs pairwise reoptimization on the poylgon with given robot initial
	position.

	Args:
		cellToSiteMap
		decomposition: A set of polygon representing the decomposition
		originalChiCosts:  List for storing original costs
		newChiCost: List for storing costs after reoptimization.
		numIterations: The number of iterations or reoptimization cuts to make
		radius: The radius of the coverage footprint
		linPenalty: A parameter used in the cost computation
		angPenalty: A parameter used in the cost computation
	Returns:
		N/A
	"""

	# Store perf stats for monitoring performance of the algorithm. 
	with open("logFile.txt", 'w') as logFile:
		chiCosts = []
		for idx, poly in enumerate(decomposition):
			cost = compute_chi(polygon = decomposition[idx],
							   initPos = cellToSiteMap[idx],
							   radius = radius,
							   linPenalty = linPenalty,
							   angPenalty = angPenalty)
			chiCosts.append((idx, cost))

		sortedChiCosts = sorted(chiCosts, key=lambda v:v[1], reverse=True)
		originalChiCosts.extend(sortedChiCosts)

		for i in range(numIterations):
			chiCosts = []
			for idx, poly in enumerate(decomposition):
				cost = compute_chi(polygon = decomposition[idx],
							initPos = cellToSiteMap[idx],
							radius = radius,
							linPenalty = linPenalty,
							angPenalty = angPenalty)
				chiCosts.append((idx, cost))
			sortedChiCosts = sorted(chiCosts, key=lambda v:v[1], reverse=True)
	
			if DEBUG_LEVEL & 0x2:
				print("Iteration: %3d/%3d: Costs: %s"%(i, numIterations, sortedChiCosts))
	
			adjacencyMatrix = compute_adjacency(decomposition)
	
			if not dft_recursion(decomposition,
								 adjacencyMatrix,
								 sortedChiCosts[0][0],
								 cellToSiteMap,
								 radius,
								 linPenalty,
								 angPenalty):
				if DEBUG_LEVEL & 0x2:
					print("Iteration: %3d/%3d: No cut was made!"%(i, numIterations))

			logFile.write("[%3d]: %s\n"%(i+1, sortedChiCosts))

		# Output new sorted costgs
		chiCosts = []
		for idx, poly in enumerate(decomposition):
			cost = compute_chi(polygon = decomposition[idx],
							   initPos = cellToSiteMap[idx],
							   radius = radius,
							   linPenalty = linPenalty,
							   angPenalty = angPenalty)
			chiCosts.append((idx, cost))
		sortedChiCosts = sorted(chiCosts, key=lambda v:v[1], reverse=True)
		newChiCosts.extend(sortedChiCosts)

		logFile.write("[%3d]: %s\n"%(i+1, sortedChiCosts))


if __name__ == '__main__':

	# If package is launched from cmd line, run sanity checks
	global DEBUG_LEVEL

	DEBUG_LEVEL = 0 #0x8+0x4

	print("\nSanity tests for the reoptimizer.\n")

	q = [(0.0,0.0),(10.0,0.0),(10.0,1.0),(0.0,1.0)]
	decomposition = [[[(0.0,0.0),(10.0,0.0), (10.0,0.5)],[]], [[(0.0,0.0),(10.0,0.5),(10.0,1.0),(5.0,0.5)],[]], [[(5.0,0.5),(10.0,1.0),(0.0,1.0)],[]], [[(0.0,0.0),(5.0,0.5),(0.0,1.0)],[]]]

	chi_reoptimize(decomposition = decomposition,
					cellToSiteMap = q)
