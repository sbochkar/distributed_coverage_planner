import numpy as np
from operator import itemgetter
from shapely.geometry import LineString

import coverage_plot as splot
from polygons import gen_poly_and_decomp

from anchored_decomposition import anchored_decomposition
from anchored_decomposition import assign_sites_to_polygon
from polygon_area import polygon_area
from convex_divide import convex_divide
import adjacency as adj
import min_alt_discrt as discrt
import chi
import min_alt_decompose as mad
import operations as op
import reflex
import cuts
import altitude as alt
from new_funks import pair_wise_reoptimization
from new_funks import reopt_recursion




DEBUG = 1
NUM_SAMPLES = 10
RADIUS = 0.1
LIN_PENALTY = 1.0
ANGULAR_PENALTY = 1.0/360




def pretty_print_decomp(decomp):
	print("[..] Decomposition:")
	for idx, poly in enumerate(decomp):
		print("%2d: "%idx),
		boundary = poly[0]
		for elem in boundary:
			print("(%.2f, %.2f), "%(elem[0],elem[1])),
		print("\n"),





# Since my decomposition tehcnique is lacking, start by hard coding the polygons and decompositions
POLY_ID = 3
orig_poly, sites, decomp = gen_poly_and_decomp(poly_id=POLY_ID)

# Compute shared edges and site assignment
cell_to_site_map = assign_sites_to_polygon(decomp, sites)
#cell_to_site_map = {0: (10,0), 1:(10,1), 2:(0,1), 3:(0,0)}
if DEBUG: 
	print("[.] Cell to Site Map: %s."%cell_to_site_map)



adj_matrix = adj.get_adjacency_as_matrix(decomp)



M = 20
iterations = 0
while iterations < M:
	iterations += 1



	chi_costs = []
	for idx, poly in enumerate(decomp):
		cost = chi.chi(polygon=decomp[idx], init_pos=cell_to_site_map[idx],
						radius=RADIUS, lin_penalty=LIN_PENALTY,
						angular_penalty=ANGULAR_PENALTY)
		chi_costs.append((idx, cost))
	chi_costs_sorted = sorted(chi_costs, key=lambda v:v[1], reverse=True)
	if DEBUG:
		print("[.] Old costs: %s"%chi_costs_sorted)

	# Begin the recursion process
	mad.collinear_correction(decomp)
	mad.post_processs_decomposition(decomp)
	adj_matrix = adj.get_adjacency_as_matrix(decomp)

	reopt_recursion.level = 0
	reopt_recursion(decomp, adj_matrix, chi_costs_sorted[0][0], cell_to_site_map)
	pretty_print_decomp(decomp)



print("[..] Plotting the original polygon and sites.")
#Initialize plotting tools
ax = splot.init_axis()
splot.plot_polygon_outline(ax, orig_poly)
splot.plot_decomposition(ax, decomp, adj_matrix, orig_poly)
splot.plot_init_poss_and_assignment(ax, sites, cell_to_site_map, decomp)
splot.display()




#if pair_wise_reoptimization(2,1, decomp, adj_matrix, cell_to_site_map):
#	if DEBUG:
#		print("[..] Reopt is performed!")
#	mad.post_processs_decomposition(decomp)
#	adj_matrix = adj.get_adjacency_as_matrix(decomp)






