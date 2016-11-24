import numpy as np
from operator import itemgetter
from shapely.geometry import LineString

import coverage_plot as splot
from polygons import generate_polygon_and_decomposition

from anchored_decomposition import anchored_decomposition, assign_sites_to_polygon
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


#Initialize plotting tools
ax = splot.init_axis()

# Since my decomposition tehcnique is lacking, start by hard coding the polygons and decompositions
NUM_POLYGON = 0
original_polygon, sites, decomposition = generate_polygon_and_decomposition(polygon_id=NUM_POLYGON)

# Compute shared edges and site assignment
cell_to_site_map = assign_sites_to_polygon(decomposition, sites)
cell_to_site_map = {0: (10,0), 1:(10,1), 2:(0,1), 3:(0,0)}
adjacency_matrix = adj.get_adjacency_as_matrix(decomposition)




print("[..] Plotting the original polygon and sites.")
splot.plot_polygon_outline(ax, original_polygon)
splot.plot_decomposition(ax, decomposition, adjacency_matrix, original_polygon)
splot.plot_init_poss_and_assignment(ax, sites, cell_to_site_map, decomposition)





splot.display()














