from math import sqrt
import numpy as np


import adjacency as adj
import min_alt_decompose as mad
import operations as op
import chi
import reflex
import cuts
from shapely.geometry import LineString


DEBUG = 1
NUM_SAMPLES = 100
RADIUS = 0.1
LIN_PENALTY = 1.0
ANGULAR_PENALTY = 1.0/360


def reopt_recursion(decomp=[], adj_matrix=[], v_max_id=0, cell_to_site_map=[]):
	"""
	This function will recursively look for the 
	"""

	reopt_recursion.level += 1
	print("[..] Recursion level: %d"%reopt_recursion.level)
	# Compute the v_max cost
	v_max_cost = chi.chi(polygon=decomp[v_max_id], init_pos=cell_to_site_map[v_max_id],
						radius=RADIUS, lin_penalty=LIN_PENALTY,
						angular_penalty=ANGULAR_PENALTY)
	if DEBUG:
		print("[.] Cell with maximum: %d, %f"%(v_max_id, v_max_cost))



	# Find adjacent cells to v_max
	neighbors = []
	for cell_id, cell in enumerate(adj_matrix[v_max_id]):
		if not cell is None:
			neighbors.append(cell_id)
	print("[.] Neighbors: %s"%(neighbors,))


	# Comptue the cost matrix for adjacent cells
	n_chi_costs = []
	for idx in neighbors:
		cost = chi.chi(polygon=decomp[idx], init_pos=cell_to_site_map[idx],
						radius=RADIUS, lin_penalty=LIN_PENALTY,
						angular_penalty=ANGULAR_PENALTY)
		n_chi_costs.append((idx, cost))

	if DEBUG:
		print("[.] Neghbours and chi: %s"%n_chi_costs)

	n_chi_costs_sorted = sorted(n_chi_costs, key=lambda v:v[1], reverse=True)

	

	for v_i_idx, n_cost in n_chi_costs:

		if n_cost < v_max_cost:
			print("[..] Attempting %d and %d."%(v_max_id, v_i_idx))
			#print decomp
			if pair_wise_reoptimization(v_max_id, v_i_idx, decomp, adj_matrix, cell_to_site_map):
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








# WIll be implementing pair-wise reoptimization step here
def pair_wise_reoptimization(cell_a_id=0, cell_b_id=0,
								decomposition=[], adj_matrix=[],
								cell_to_site_map=[]):
	"""
	This function will take one two adjacent polygons and attempt to find a new cut
	that improves the maximum cost.

	This function modifies decomposition and cell_to_site_map
	
	"""
	DEBUG = 1
	NUM_SAMPLES = 100
	RADIUS = 0.1
	LIN_PENALTY = 1.0
	ANGULAR_PENALTY = 1.0/360

	# Sanity check: two polygons are adjancent
	if not adj_matrix[cell_a_id][cell_b_id]:
		print("[..]!!! Pair-wise reopt: The polygons are not adjacent.")
		return


	# Record the costs at this point
	# Now start evaluating the polygons
	chi_l = chi.chi(polygon=decomposition[cell_a_id],
						init_pos=cell_to_site_map[cell_a_id],
						radius=RADIUS,
						lin_penalty=LIN_PENALTY,
						angular_penalty=ANGULAR_PENALTY)
	chi_r = chi.chi(polygon=decomposition[cell_b_id],
						init_pos=cell_to_site_map[cell_b_id],
						radius=RADIUS,
						lin_penalty=LIN_PENALTY,
						angular_penalty=ANGULAR_PENALTY)
	max_chi = max(chi_l, chi_r)
	old_max_chi = max_chi


	# Combine the polygons
	#print decomposition[cell_a_id]
	#print decomposition[cell_b_id]
	#print adj_matrix[cell_a_id][cell_b_id]
	cell_union = op.union_two_cells(decomposition[cell_a_id], decomposition[cell_b_id],
									adj_matrix[cell_a_id][cell_b_id])
	if DEBUG: 
		print("[..] Cell Union: %s."%cell_union)

	# If there is a refelx vertex present in the union, it may be sensible to
	# 	choose it as a strating point for a cut.
	shared_edge = adj_matrix[cell_a_id][cell_b_id]
	reflex_verts = reflex.find_reflex_vertices(cell_union)
	if not reflex_verts:
		v_s = (cell_union[0].index(shared_edge[0]), shared_edge[0]) #v_s is (idx, (x,y))
		is_reflex = False
	else:
		v_s = reflex_verts[0]
		is_reflex = True
	if DEBUG: 
		print("[..] Cut pivot: %s. Reflex?: %s"%(v_s[1], is_reflex))


	# Find the cut space from v_s, SHOULD BE STABLE ENOUGH AT THIS POINT
	cut_space = cuts.find_cut_space(cell_union, v_s, is_reflex=is_reflex)
	if DEBUG: 
		print("[..] Cut Space: %s."%cut_space)

	# Sample each edge in the cut space with K samples
	samples = []
	for line in cut_space:
		line_ls = LineString(line)
		sample_distances = list(np.linspace(0,line_ls.length, NUM_SAMPLES))
		temp_samples = [(line_ls.interpolate(i).x,
							line_ls.interpolate(i).y) for i in sample_distances]
		samples.extend(temp_samples)
	if DEBUG: 
		print("[..] Number of samples: %d."%len(samples))



	# Now start generating all kinds of cuts from v_s to sample
	v_e = []
	for sample in samples:
		cut = (v_s[1], sample)
		# Check if the cut is valid or not first
		if LineString(cut).length == 0:
			continue

		p_l, p_r = cuts.perform_cut(cell_union, cut)
		if not p_r:
			continue
		# Quick and dirty method to eliminate edge cases
		if len(p_r) < 3 or len(p_l) < 3:
			continue

		# Check if the polygons are self-intersecting
		if not LineString(p_r).is_simple:
			print "self intersecting"
			continue
		if not LineString(p_l).is_simple:
			print "self intersecting"
			continue

		# Because I lost the relationship between what site belongs to what
		# 	I need to recompute that
		boundary_l = list(p_l)
		boundary_r = list(p_r)
	
		site_1 = cell_to_site_map[cell_a_id] 
		site_2 = cell_to_site_map[cell_b_id]
	
		boundary_l.sort(key=lambda v: (site_1[0]-v[0])**2+(site_1[1]-v[1])**2)
		boundary_r.sort(key=lambda v: (site_1[0]-v[0])**2+(site_1[1]-v[1])**2)
		closest_l = boundary_l[0]
		closest_r = boundary_r[0]
		dist_l_to_1 = (site_1[0]-boundary_l[0][0])**2+(site_1[1]-boundary_l[0][1])**2
		dist_r_to_1 = (site_1[0]-boundary_r[0][0])**2+(site_1[1]-boundary_r[0][1])**2


		boundary_l.sort(key=lambda v: (site_2[0]-v[0])**2+(site_2[1]-v[1])**2)
		boundary_r.sort(key=lambda v: (site_2[0]-v[0])**2+(site_2[1]-v[1])**2)
		closest_l = boundary_l[0]
		closest_r = boundary_r[0]
		dist_l_to_2 = (site_2[0]-boundary_l[0][0])**2+(site_2[1]-boundary_l[0][1])**2
		dist_r_to_2 = (site_2[0]-boundary_r[0][0])**2+(site_2[1]-boundary_r[0][1])**2

		if dist_l_to_1 + dist_r_to_2 < dist_l_to_2 + dist_r_to_1:
			l_site = site_1
			r_site = site_2
		else:
			l_site = site_2
			r_site = site_1


		# Now start evaluating the polygons
		chi_l = chi.chi(polygon=[p_l,[]],
							init_pos=l_site,
							radius=RADIUS,
							lin_penalty=LIN_PENALTY,
							angular_penalty=ANGULAR_PENALTY)
		chi_r = chi.chi(polygon=[p_r,[]],
							init_pos=r_site,
							radius=RADIUS,
							lin_penalty=LIN_PENALTY,
							angular_penalty=ANGULAR_PENALTY)

		if max(chi_l, chi_r) < max_chi:
			max_chi = max(chi_l, chi_r)
			v_e = sample
			min_l_site = l_site
			min_r_site = r_site


	# Once the search space has been exhausted check if any cuts were made
	if v_e:
		cut = (v_s[1], v_e)
		p_l, p_r = cuts.perform_cut(cell_union, cut)

		# Except the sites might change, so I need to do it smartly unfortenately
		decomposition[cell_a_id] = [p_l, []]
		decomposition[cell_b_id] = [p_r, []]
		cell_to_site_map[cell_a_id] = min_l_site
		cell_to_site_map[cell_b_id] = min_r_site

		if DEBUG:
			print("[..] Improving cut was found: %s"%(cut,))
			print("[..] Max cost Before: %f Now: %f"%(old_max_chi,max_chi))

		return True
	else:
		print("[..] Improving cut was NOT found: %s"%(cut,))
		return False