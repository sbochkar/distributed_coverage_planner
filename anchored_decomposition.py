from operator import itemgetter
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
from shapely.geometry import LineString
import numpy as np


NUM_SAMPLES = 10


def assign_sites_to_polygon(decomposition=[], sites=[]):
	"""
	Use min distance to vertex condition to assign sites to decomp
	"""

	decomp_to_site_map = {}
	site_queue = list(sites)

	for poly_id, poly in enumerate(decomposition):

		min_dist_so_far = 10e10
		closest_site_id = -1
		boundary = poly[0]
		
		for site_id, site in enumerate(site_queue):
			x, y = site
			verts_sorted_by_dist = sorted([(x-v[0])**2+(y-v[1])**2 for v in boundary])
			vert_site_dist = verts_sorted_by_dist[0]

			if vert_site_dist < min_dist_so_far:
				min_dist_so_far = vert_site_dist
				closest_site_id = site_id

		# Assign the closest site to the current poly
		decomp_to_site_map[poly_id] = site_queue[closest_site_id]
		site_queue.pop(closest_site_id)

	return decomp_to_site_map




def anchored_decomposition(polygon=[[],[]], init_poss=[]):
	"""
	Perform convex divide n times
	Assume that area is split equally
	"""

	decomposition = []
	site_to_cell_map = []
	queue_polygon = [{"polygon":polygon,"sites":init_poss}]

	if len(init_poss) == 1:
		return polygon

	while len(decomposition)<len(init_poss):

		# Compute area req based on area and number of sites

		test_poly = queue_polygon.pop()

		area_req = polygon_area(test_poly["polygon"])/len(test_poly["sites"])
		p_r, p_l = convex_divide(polygon=test_poly["polygon"],
									init_poss=test_poly["sites"],
									area_req=area_req)

		
		if len(p_r["sites"]) == 1:
			decomposition.append(p_r["polygon"])
			site_to_cell_map.append((p_r["sites"][0], len(decomposition)-1))
		else:
			queue_polygon.append(p_r)

		if len(p_l["sites"]) == 1:
			decomposition.append(p_l["polygon"])
			site_to_cell_map.append((p_l["sites"][0], len(decomposition)-1))
		else:
			queue_polygon.append(p_l)



	return decomposition, site_to_cell_map



def actually_do_decomposition():

	P = [[(0.0, 0.0),(4.0, 0.0),(4.0, 4.0),(6.0, 4.0),(6.0, 0.0),(10.0, 0.0),(10.0, 6.0),(8.0, 7.0),(7.5, 8.0),(10.0, 7.5),(10.0, 10.0),(0.0, 10.0),(0.0, 5.0),(5.0, 6.0),(5.0, 5.0),(0.0, 4.0)],[]]
	#P = [[(0,0),(10,0),(10,1),(0,1)],[]]
	P = [[(1,0),(2,0),(3,1),(3,2),(2,3),(1,3),(0,2),(0,1)],[]]
	q = [(1,-1),(2,-1),(3,3),(0,3)]
	#q = [(0,10),(10,0),(10,1),(0,1)]

	# This is the initial step to start the optimization procedure
	decomposition, site_to_cell_map = anchored_decomposition(polygon=P, init_poss=q)
	print decomposition
	old_decomposition = list(decomposition)
	# Should really e using this for looking for shared edges and stuff
	#processed_decomposition = mad.post_processs_decomposition(decomposition)
	decomposition = mad.post_processs_decomposition(decomposition)

	# For now do two iterations
	for i in range(1):

		# Comptue an adjacency matrix for the current decomposition
		adjacency_matrix = adj.get_adjacency_as_matrix(decomposition)
		# Site_to_cell_map: maps the coord from init_poss to the index of assigned cell. ((x,y), idx)
		site_to_cell_map.sort(key=lambda v:v[1])


		# Construct a list of chi metric for each cell and its assigned site
		# chi_storage: chi values for each cell and the index of the cell as it appears in decomposition in the accending order
		chi_costs = [(idx, chi.chi(polygon=decomposition[idx], init_pos=site, radius=0.1, lin_penalty=1.0, angular_penalty=1.0/360.0)) for site, idx in site_to_cell_map]
		chi_costs_sorted = sorted(chi_costs, key=lambda v:v[1], reverse=True)
		print("Old costs: %s"%chi_costs)

		# First find the cell with the highest cost
		highest_cost_cell_id = chi_costs_sorted[0][0]
		highest_cost_cell_site_id = site_to_cell_map[highest_cost_cell_id] # Tuple ((x,y), cell_id)

		# Now find an adjacent cell with the lowest cost
		adjacent_cells = []	# Just a list of indecies signifying the adjacent cells
		for idx, cell in enumerate(adjacency_matrix[highest_cost_cell_id]):
			if cell is not None:
				adjacent_cells.append(idx)


		adjacent_chi_costs = sorted([(i, chi_costs[i][1]) for i in adjacent_cells],key=lambda v:v[1])
		for lowest_cost_cell_id, temp in adjacent_chi_costs:
			print highest_cost_cell_id, lowest_cost_cell_id
			lowest_cost_cell_site_id = site_to_cell_map[lowest_cost_cell_id] # Tuple ((x,y), cell_id)




			# Now we perform the polygon modifications
			shared_edge = adjacency_matrix[highest_cost_cell_id][lowest_cost_cell_id]
			# Combine the two polygons
			cell_union = [op.combine_two_adjacent_polys(decomposition[highest_cost_cell_id][0],
														decomposition[lowest_cost_cell_id][0],
														adjacency_matrix[highest_cost_cell_id][lowest_cost_cell_id]),[]]
			#print cell_union
			# Find the reflex vertecies in the cell union, it may be beneficial to make cuts from the reflex verts
			reflex_verts = reflex.find_reflex_vertices(cell_union)
			if not reflex_verts:
				v_s = (cell_union[0].index(shared_edge[0]), shared_edge[0]) #v_s is (idx, (x,y))
				is_reflex = False
			else:
				v_s = reflex_verts[0]
				is_reflex = True
	

			# Find the cut space from v_s
			#print cell_union, v_s
			cut_space = cuts.find_cut_space(cell_union, v_s, is_reflex=is_reflex)
			cut_space_points=[]
			for segment in cut_space:
				cut_space_points.extend(segment)
			cut_space_ls = LineString(cut_space_points)
			#print cut_space_ls



			#print highest_cost_cell_id, lowest_cost_cell_id
			#print decomposition
			# Now sample the cut space 
			cut_space_length = cut_space_ls.length
			#step_size = cut_space_length/float(NUM_SAMPLES)
			#samples = list(np.arange(step,s_length-step, step))
			sample_distances = list(np.linspace(0,cut_space_length, NUM_SAMPLES))
			samples = [(cut_space_ls.interpolate(i).x,cut_space_ls.interpolate(i).y) for i in sample_distances]




			# Evaluate the cost for each cut endpoint in samples
			chi_costs = []
			v_e = []
			#max_chi = 10e10
			max_chi = max(chi_costs_sorted[0][1], adjacent_chi_costs[0][1])
			#print max_chi
			for sample in samples:
				# Choose cut and perform the cut
				cut = (v_s[1], sample)
				# Check if the cut is valid or not first
				if LineString(cut).length == 0:
					continue
				#print cut
				p_l, p_r = cuts.perform_cut(cell_union, cut)
				if len(p_r) < 3 or len(p_l) < 3: # QUick and dirty method to eliminate edge cases
					continue


				# Because I lost the relationship between what site belongs to what I need to recompute that
				boundary_l = list(p_l)
				boundary_r = list(p_r)
	
				site_1 = highest_cost_cell_site_id[0] 
				site_2 = lowest_cost_cell_site_id[0]
	
				boundary_l.sort(key=lambda v: (site_1[0]-v[0])**2+(site_1[1]-v[1])**2)
				boundary_r.sort(key=lambda v: (site_1[0]-v[0])**2+(site_1[1]-v[1])**2)
				closest_l = boundary_l[0]
				closest_r = boundary_r[0]
				dist_l_to_1 = (site_1[0]-boundary_l[0][0])**2+(site_1[1]-boundary_l[0][1])**2
				dist_t_to_1 = (site_1[0]-boundary_r[0][0])**2+(site_1[1]-boundary_r[0][1])**2
	
	
				boundary_l.sort(key=lambda v: (site_2[0]-v[0])**2+(site_2[1]-v[1])**2)
				boundary_r.sort(key=lambda v: (site_2[0]-v[0])**2+(site_2[1]-v[1])**2)
				closest_l = boundary_l[0]
				closest_r = boundary_r[0]
				dist_l_to_2 = (site_2[0]-boundary_l[0][0])**2+(site_2[1]-boundary_l[0][1])**2
				dist_r_to_2 = (site_2[0]-boundary_r[0][0])**2+(site_2[1]-boundary_r[0][1])**2
	
				if dist_l_to_1 <= dist_l_to_2:
					l_site = site_1
					r_site = site_2
				else:
					l_site = site_2
					r_site = site_1
				#print("P_l: %s"%p_l)
				chi_l = chi.chi(polygon=[p_l,[]],
									init_pos=l_site,
									radius=0.1,
									lin_penalty=1.0,
									angular_penalty=1.0/360.0)
				chi_r = chi.chi(polygon=[p_r,[]],
									init_pos=r_site,
									radius=0.1,
									lin_penalty=1.0,
									angular_penalty=1.0/360.0)

				#print max(chi_l, chi_r)
				if max(chi_l, chi_r) < max_chi:
					max_chi = max(chi_l, chi_r)
					v_e = sample
				#print highest_cost_cell_id, lowest_cost_cell_id



			# At this point, an optimal cut is found, so we can actually make the cut
			if v_e:
				print "CUTS ARE BEING MADE"
				cut = (v_s[1], v_e)
				p_l, p_r = cuts.perform_cut(cell_union, cut)

				# Except the sites might change, so I need to do it smartly unfortenately
				decomposition[highest_cost_cell_id] = [p_l,[]]
				decomposition[lowest_cost_cell_id] = [p_r, []]

				#print highest_cost_cell_id, lowest_cost_cell_id
				chi_costs_t = [(idx, chi.chi(polygon=decomposition[idx], init_pos=site, radius=0.1, lin_penalty=1.0, angular_penalty=1.0/360.0)) for site, idx in site_to_cell_map]
				print("New costs: %s\n"%chi_costs_t)
				break
			else:
				pass








	#samples = list(xrange(s_length, 100))













	#cut = cuts.find_optimal_cut([cell_union,[]], v_s)
	#print cut
	#print processed_decomposition
	#print decomposition[highest_cost_cell_id]
	#print decomposition[lowest_cost_cell_id]
	#print shared_edge



	adjacency_matrix = adj.get_adjacency_as_matrix(decomposition)
	#segments = discrt.discritize_set(decomposition, 0.1)


	#return
	import coverage_plot as splot
	ax = splot.init_axis()
	splot.plot_decomposition(ax, decomposition, adjacency_matrix, P)
	#splot.plot_decomposition(ax, old_decomposition, [], P)
	#splot.plot_samples(ax, segments)
	splot.plot_init_poss(ax, q)
	splot.display()


if __name__ == "__main__":
	actually_do_decomposition()




#	elif map_num == 11:
#		ext = [(0.0,   0.0),
#				(6.0,  0.0),
#				(6.0,  5.0),
#				(4.0,  5.0),
#				(4.0,  3.0),
#				(5.0,  3.0),
#				(5.0,  2.0),
#				(3.0,  2.0),
#				(3.0,  6.0),
#				(7.0,  6.0),
#				(7.0,  0.0),
#				(10.0, 0.0),
#				(10.0, 10.0),
#				(0.0,  10.0)
#				]
#
#		holes = [
#					[
#						(4.0, 7.0),
#						(3.5, 8.0),
#						(4.5, 9.0),
#						(6.0, 8.0)
#					]
#				]