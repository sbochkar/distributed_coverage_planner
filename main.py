import coverage_plot as splot

from polygons import gen_poly_and_decomp
from decomposition_processing import compute_adjacency
from chi import compute_chi
from reopt_recursion import dft_recursion
from polygon_area import polygon_area
from reoptimizer import chi_reoptimize


GLKH_LOCATION = "/home//misc/GLKH-1.0/"

POLY_ID = 3
NUM_SAMPLES = 10
NUM_REOPT_ITERATIONS = 5
RADIUS = 0.2
LINEAR_PENALTY = 1.0
ANGULAR_PENALTY = 100*1.0/360
DEBUG_LEVEL = 0



def pretty_print_decomposition(decomposition):
	print("[..] decompositionosition:")
	for idx, poly in enumerate(decomposition):
		print("%2d: "%idx),
		boundary = poly[0]
		for elem in boundary:
			print("(%.2f, %.2f), "%(elem[0],elem[1])),
		print("\n"),


def distributed_planner(polyId = 0, numReoptIters = 10):
	# Assume that robots are assigned to the cells nearest to them.
	# Otherwise, we can just run matching algorithm.
	# Todo: Implement the matching algorithm to find the best matching
	#       at every iteration that results in lower cost.
	polygon, cellToSiteMap, decomposition = gen_poly_and_decomp(polyId)
	oldDecomposition = list(decomposition)

	oldCosts = []
	newCosts = []

	print("Reoptimizing polygon: %3d"%polyId)
	print("Attempting %d reoptimization iterations."%numReoptIters)
	chi_reoptimize(decomposition,
				   cellToSiteMap,
				   oldCosts,
				   newCosts,
				   numIterations = numReoptIters,
				   radius = RADIUS,
				   linPenalty = LINEAR_PENALTY,
				   angPenalty = ANGULAR_PENALTY)
	print("Old costs: %s"%oldCosts)
	print("New costs: %s"%newCosts)


	# For this step, need to implement minimum altitude decomposition
	# For now, just plan a path for each robot
	#minAltDecomposition = []
	#for polygon in decomposition:

		#from reflex import find_reflex_vertices
		#reflexVerts = reflex.find_reflex_vertices(P)
		#compute_min_alt_cut(polygon, reflexVertex)
		#minAltDecomposition.append(min_alt(polygon))



	# Start visuals
	# Initialize plotting tools
	axOld = splot.init_axis("Original Decomposition", "+0+100")
	axNew = splot.init_axis("Reoptimized Decomposition", "+700+100")

	# Populate the drawing canvas
	splot.plot_polygon_outline(axOld, polygon)
	splot.plot_polygon_outline(axNew, polygon)

	splot.plot_decomposition(axOld, oldDecomposition)
	splot.plot_decomposition(axNew, decomposition)

	splot.plot_init_pos_and_assignment(axOld, cellToSiteMap, oldDecomposition)
	splot.plot_init_pos_and_assignment(axNew, cellToSiteMap, decomposition)

	# Send the plot command
	splot.display()





#segments = discrt.discritize_set(decomposition, radius)
#mapping = get_mapping.get_mapping(segments)
#cost_matrix, cluster_list = dubins_cost.compute_costs(orig_poly, mapping, radius/2)
#solver.solve("cpp_test", GLKH_LOCATION, cost_matrix, cluster_list)
#tour = solver.read_tour("cpp_test")
#print cellToSiteMap

#single_planner.single_planner(decomposition, radius, orig_poly, cellToSiteMap)

#Initialize plotting tools



#splot.plot_samples(ax, segments)
#splot.plot_tour_dubins(ax, tour, mapping, RADIUS/2)
#splot.display()

if __name__ == '__main__':

	# If package is launched from cmd line, run sanity checks
	distributed_planner(POLY_ID, NUM_REOPT_ITERATIONS)