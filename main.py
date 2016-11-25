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


DEBUG = 1
NUM_SAMPLES = 10
RADIUS = 0.1
LIN_PENALTY = 1.0
ANGULAR_PENALTY = 1.0/360
#Initialize plotting tools
ax = splot.init_axis()

# Since my decomposition tehcnique is lacking, start by hard coding the polygons and decompositions
POLY_ID = 1
orig_poly, sites, decomp = gen_poly_and_decomp(poly_id=POLY_ID)

# Compute shared edges and site assignment
cell_to_site_map = assign_sites_to_polygon(decomp, sites)
#cell_to_site_map = {0: (10,0), 1:(10,1), 2:(0,1), 3:(0,0)}
if DEBUG: 
	print("[..] Cell to Site Map: %s."%cell_to_site_map)

adj_matrix = adj.get_adjacency_as_matrix(decomp)



print pair_wise_reoptimization(2, 1, decomp, adj_matrix, cell_to_site_map)



print("[..] Plotting the original polygon and sites.")
splot.plot_polygon_outline(ax, orig_poly)
splot.plot_decomposition(ax, decomp, adj_matrix, orig_poly)
splot.plot_init_poss_and_assignment(ax, sites, cell_to_site_map, decomp)





splot.display()














