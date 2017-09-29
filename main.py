import numpy as np
from operator import itemgetter

from shapely.geometry import LineString
from shapely.geometry import LinearRing

import coverage_plot as splot
from polygons import gen_poly_and_decomp

from polygon_area import polygon_area
from convex_divide import convex_divide
from decomposition_processing import compute_adjacency
from chi import compute_chi
from reopt_recursion import dft_recursion
#import min_alt_discrt as discrt
#import chi
#import min_alt_decompositionose as mad
#import operations as op
#import reflex
#import cuts
#import altitude as alt
#import get_mapping
#import dubins_cost
#import solver
#import single_planner


GLKH_LOCATION = "/home//misc/GLKH-1.0/"

DEBUG = []
NUM_SAMPLES = 10
NUM_ITERATIONS = 5
RADIUS = 0.2
LINEAR_PENALTY = 1.0
ANGULAR_PENALTY = 10*1.0/360
DEBUG_LEVEL = 0



def pretty_print_decomposition(decomposition):
	print("[..] decompositionosition:")
	for idx, poly in enumerate(decomposition):
		print("%2d: "%idx),
		boundary = poly[0]
		for elem in boundary:
			print("(%.2f, %.2f), "%(elem[0],elem[1])),
		print("\n"),





# Since my decompositionosition tehcnique is lacking, start by hard coding the polygons and decompositionositions
POLY_ID = 5
orig_poly, sites, decomposition = gen_poly_and_decomp(poly_id=POLY_ID)

# Compute shared edges and site assignment
#cellToSiteMap = assign_sites_to_polygon(decomposition, sites)
cellToSiteMap = {0: (10,0), 1:(10,1), 2:(0,1), 3:(0,0)}
if DEBUG: 
	print("[.] Cell to Site Map: %s."%cellToSiteMap)


# Output initial sorted costs
chiCosts = []
for idx, poly in enumerate(decomposition):
	cost = compute_chi(polygon = decomposition[idx],
					   initPos = cellToSiteMap[idx],
					   radius = RADIUS,
					   linPenalty = LINEAR_PENALTY,
					   angPenalty = ANGULAR_PENALTY)
	chiCosts.append((idx, cost))
sortedChiCosts = sorted(chiCosts, key=lambda v:v[1], reverse=True)
print("[.] Initial costs: %s"%sortedChiCosts)


#	Run the optimization procedure for NUM_ITERATIONS
for i in range(NUM_ITERATIONS):

	chiCosts = []
	for idx, poly in enumerate(decomposition):
		cost = compute_chi(polygon = decomposition[idx],
						   initPos = cellToSiteMap[idx],
						   radius = RADIUS,
						   linPenalty = LINEAR_PENALTY,
						   angPenalty = ANGULAR_PENALTY)
		chiCosts.append((idx, cost))
	sortedChiCosts = sorted(chiCosts, key=lambda v:v[1], reverse=True)

	if DEBUG_LEVEL & 0x8:
		print("[.] Old costs: %s"%sortedChiCosts)

	adjacencyMatrix = compute_adjacency(decomposition)

	if not dft_recursion(decomposition,
						 adjacencyMatrix,
						 sortedChiCosts[0][0],
						 cellToSiteMap):
		print("[%3d/%3d] No cut was made!"%(i, NUM_ITERATIONS))

# Output new sorted costgs
chiCosts = []
for idx, poly in enumerate(decomposition):
	cost = compute_chi(polygon = decomposition[idx],
					   initPos = cellToSiteMap[idx],
					   radius = RADIUS,
					   linPenalty = LINEAR_PENALTY,
					   angPenalty = ANGULAR_PENALTY)
	chiCosts.append((idx, cost))
sortedChiCosts = sorted(chiCosts, key=lambda v:v[1], reverse=True)
print("[.] New costs: %s"%sortedChiCosts)



print("[..] Plotting the original polygon and sites.")
adjacencyMatrix = compute_adjacency(decomposition)
print("New decomposition: %s"%decomposition)


#segments = discrt.discritize_set(decomposition, RADIUS)
#mapping = get_mapping.get_mapping(segments)
#cost_matrix, cluster_list = dubins_cost.compute_costs(orig_poly, mapping, RADIUS/2)
#solver.solve("cpp_test", GLKH_LOCATION, cost_matrix, cluster_list)
#tour = solver.read_tour("cpp_test")
#print cellToSiteMap

#single_planner.single_planner(decomposition, RADIUS, orig_poly, cellToSiteMap)

#Initialize plotting tools
#ax = splot.init_axis()
#splot.plot_polygon_outline(ax, orig_poly)
#splot.plot_decompositionosition(ax, decomposition, adj_matrix, orig_poly)
#splot.plot_init_poss_and_assignment(ax, sites, cellToSiteMap, decomposition)
#splot.plot_samples(ax, segments)
#splot.plot_tour_dubins(ax, tour, mapping, RADIUS/2)
#splot.display()