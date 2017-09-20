from shapely.geometry import Polygon

from chi import compute_chi


RADIUS = 0.1
LINEAR_PENALTY = 1		# Weights for the cost function
ANGULAR_PENALTY = 10	# Weights for the cost function


def compute_pairwise_optimal(polygonA=[],
							 polygonB=[],
							 robotAInitPos=[],
							 robotBInitPos=[]):
	"""
	Takes two adjacent polygons and attempts to modify the shared edge such that
	the metric chi is reduced.

	Args:
		cell_a_id:
		cell_b_id:
		decomposition:
		adj_matrix:
		cell_to_site_map:

	Returns:
		:
	
	"""

	# Issues:
	#	1) Why do we need the adjacent matrix
	#	2) Why do we need cell to site map?


    # Check if they are adjacent
    # Check if the touch and do not overlap
    # Check if they are not empty
    # Check that they are valid
    # And so on

	# The actual algorithm:
	# 1) Combine the two polygons
	# 2) Find one cut that works better
	# 3) Return that cut or no cut if nothing better was found

	if not polygonA or not polygonB:
		if DEBUG_LEVEL & 0x04:
			print("Pairwise reoptimization is requested on an empty polygon.")
		return []

	if not robotAInitPos or not robotBInitPos:
		if DEBUG_LEVEL & 0x04:
			print("Pairwise reoptimization is requested on an empty init pos.")
		return []

	if not Polygon(*polygonA).is_valid or not Polygon(*polygonB).is_valid:
		if DEBUG_LEVEL & 0x04:
			print("Pariwise reoptimization is requested on invalid polygons.")
		return []

	if not Polygon(*polygonA).is_valid or not Polygon(*polygonB).is_valid:
		if DEBUG_LEVEL & 0x04:
			print("Pariwise reoptimization is requested on invalid polygons.")
		return []

	if not Polygon(*polygonA).is_simple or not Polygon(*polygonB).is_simple:
		if DEBUG_LEVEL & 0x04:
			print("Pariwise reoptimization is requested on nonsimple polygons.")
		return []

	if not Polygon(*polygonA).touches(Polygon(*polygonB)):
		if DEBUG_LEVEL & 0x04:
			print("Pariwise reoptimization is requested on nontouching polys.")
		return []


	# Check that the polygons intersect only at the boundary and one edge
	intersection = Polygon(*polygonA).intersection(Polygon(*polygonB))


	if type(intersection) is not LinearString:
		if DEBUG_LEVEL & 0x04:
			print("Pariwise reoptimization is requested but they don't touch\
				   at an edge.")
		return []


	# Combine the two polygons
	polygonUnion = Polygon(*polygonA).union(Polygon(*polygonB))


	if not polygonUnion.is_valid or not polygonUnion.is_simple:
		if DEBUG_LEVEL & 0x04:
			print("Pariwise reoptimization is requested but the union resulted\
				   in bad polygon.")
		return []

	if type(polygonUnion) is not Polygon:
		if DEBUG_LEVEL & 0x04:
			print("Pariwise reoptimization is requested but union resulted in\
				   non polygon.")
		return []











	# Record the costs at this point
	# Now start evaluating the polygons
	chi_l = compute_chi(polygon=decomposition[cell_a_id],
						init_pos=cell_to_site_map[cell_a_id],
						radius=RADIUS,
						lin_penalty=LIN_PENALTY,
						angular_penalty=ANGULAR_PENALTY)
	chi_r = compute_chi(polygon=decomposition[cell_b_id],
						init_pos=cell_to_site_map[cell_b_id],
						radius=RADIUS,
						lin_penalty=LIN_PENALTY,
						angular_penalty=ANGULAR_PENALTY)
	max_chi = max(chi_l, chi_r)
	old_max_chi = max_chi




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


	if reflex_verts:
		v_e = []
		v_s_fixed = []
		#for v_s in [v_s]:
		for idx, v_s in enumerate(reflex_verts):
			# Find the cut space from v_s, SHOULD BE STABLE ENOUGH AT THIS POINT
			#print cell_union
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
				if not LinearRing(p_r).is_simple:
					if DEBUG:
						print "self intersecting"
					continue
				if not LinearRing(p_l).is_simple:
					if DEBUG:
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
					v_s_fixed = v_s[1]
					min_l_site = l_site
					min_r_site = r_site

	else:
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
		v_s_fixed = []
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
			if not LinearRing(p_r).is_simple:
				if DEBUG:
					print "self intersecting"
				continue
			if not LinearRing(p_l).is_simple:
				if DEBUG:
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
				v_s_fixed = v_s[1]
				min_l_site = l_site
				min_r_site = r_site



	# Once the search space has been exhausted check if any cuts were made
	if v_e:
		#cut = (v_s[1], v_e)
		cut = (v_s_fixed, v_e)
		p_l, p_r = cuts.perform_cut(cell_union, cut)
		# Check if the polygons are self-intersecting
		if not LinearRing(p_r).is_simple:
			if DEBUG:
				print "SANITY CHECKING FAILED. RIGHT"
		if not LinearRing(p_l).is_simple:
			if DEBUG:
				print "SANITY CHECKING FAILED, LEFT"


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
		if DEBUG:
			print("[..] Improving cut was NOT found: %s"%(cut,))
		return False


if __name__ == '__main__':

	# If package is launched from cmd line, run sanity checks
	global DEBUG_LEVEL

	DEBUG_LEVEL = 0 #0x8+0x4

	print("\nSanity tests for pairwise reoptimization\n.")

