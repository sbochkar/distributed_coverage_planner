import min_alt_discrt as discrt
import get_mapping
import dubins_cost
import solver
import greedy_decompose
import adjacency
import coverage_plot as splot
import min_alt_decompose
import classes
import tour_length
import tour_area
from shapely.geometry import LineString


GLKH_LOCATION = "/home/sbochkar/misc/GLKH-1.0/"


def single_planner(decomp, radius=1.0, orig_poly=[], cell_to_site_map=[]):
	"""
	Single agent path planner:
	"""

	single_decomposition_list = []
	adj_matrix_list = []
	segment_list = []
	map_list = []
	tours = []
	print cell_to_site_map[1]
	for idx, region in enumerate(decomp):

		#single_decomp = greedy_decompose.decompose(region)
		#single_decomp = min_alt_decompose.decompose(region)
		if not LineString(region[0]).is_simple:
			print("[!!] Passing a polygon that is self intersecting.")
			
		single_decomposition_list.append(min_alt_decompose.decompose(region))
		#adjacency_matrix = adjacency.get_adjacency_as_matrix(single_decomposition_list[-1])
		adj_matrix_list.append(adjacency.get_adjacency_as_matrix(single_decomposition_list[-1]))


		segments = discrt.discritize_set(single_decomposition_list[-1], radius)
		segments.append(classes.PointSegment((cell_to_site_map[idx])))
		segment_list.append(segments)
		#mapping = get_mapping.get_mapping(segments)
		map_list.append(get_mapping.get_mapping(segment_list[-1]))
		cost_matrix, cluster_list = dubins_cost.compute_costs(region, map_list[-1], radius/2, orig_poly)
		solver.solve("cpp_test", GLKH_LOCATION, cost_matrix, cluster_list)
		#tour = solver.read_tour("cpp_test")
		tours.append(solver.read_tour("cpp_test"))

		print("Tour Length %2f."%tour_length.length(tours[-1], segments, cost_matrix))
		#splot.display()
		#print("Polygon Area: %2f"%tour_area.polygon_area(P))
		#print("Area covered: %2f"%tour_area.covered_area(tour, mapping, width/2))



	#Initialize plotting tools
	ax = splot.init_axis()
	for idx, region in enumerate(decomp):
		splot.plot_polygon_outline(ax, region, idx)
		splot.plot_decomposition(ax, single_decomposition_list[idx], adj_matrix_list[idx], region)
		splot.plot_samples(ax, segment_list[idx], idx)
		splot.plot_tour_dubins(ax, tours[idx], map_list[idx], radius/2, idx)

	sites = [points for idx, points in cell_to_site_map.items()]
	splot.plot_main_polygon(ax, orig_poly)
	#splot.plot_init_poss_and_assignment(ax, sites, cell_to_site_map, decomp)
	splot.display()


	return []