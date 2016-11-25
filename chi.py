from math import sqrt

from shapely.geometry import LinearRing
from shapely.geometry import LineString
from shapely.geometry import Polygon

from polygon_area import polygon_area

def chi(polygon=[[],[]], init_pos=(0,0), radius=1, lin_penalty=1.0, angular_penalty=1.0):
	"""
	Metric chi: Approximation of the cost of a coverage path for a polygon P

	F1=distance from q to P and back
	F2=sum of lengths of straight line segments
	F3=approximation of the angular component of P

	P = (Z_0,Z_1,...)
	"""


	F1 = 2*min_dist_to_boundary(polygon, init_pos)
	F2 = polygon_area(polygon)/radius  #O(n)
	F3 = 360.0*compute_num_contours(polygon=polygon, radius=radius)

	return lin_penalty*(F1+F2)+angular_penalty*F3


def min_dist_to_boundary(polygon=[[],[]], init_pos=(0,0)):
	"""
	Compute shortest distance from init_pos to vertex of polygon

	"""

	boundary = polygon[0]
	
	# Get the distance between closest vertex in boundary of P to q
	# O(nlogn)

	x, y = init_pos
	vertex_dists = sorted([(x-v[0])**2+(y-v[1])**2 for v in boundary])
	closest_dist = sqrt(vertex_dists[0])

	return closest_dist



def compute_num_contours(polygon=[[],[]], radius=1):
	"""
	Computing contours of P

	Uses shapely library
	P=(z0,z1,...)
	"""

	test_polygon = Polygon(*polygon)

	num_contours = 0
	while not test_polygon.buffer(-(2*num_contours+1)*radius/2.0).is_empty:
		num_contours += 1

	return num_contours

	#boundary = LinearRing(polygon[0])
	#boundary = LineString(polygon[0])
	#boundary = LineString(polygon[0]+[polygon[0][0]])
	#print("Boundary: %s"%boundary)
	# Since working on the boundary, left should be valid all the time
	#num_contours = 0
	#new_contour = boundary.parallel_offset((2*num_contours+1)*radius/2.0, 'left', resolution=20, mitre_limit=2.0)
	#while new_contour.is_empty:
	#	if num_contours>50:
	#		print "parallel_offset did not coverge"
	#		break
		
	#	num_contours += 1
	#	new_contour = boundary.parallel_offset((2*num_contours+1)*radius/2.0, 'left', resolution=1)

	#return num_contours	




#P = [[(0,0),(1,0),(1,1),(0,1)],[]]
#P = [[(0,0),(10,0),(10,1),(0,1)],[]]
#q = (-1,-1)
#r = 0.5

#print chi(polygon=P, init_pos=q, radius=r, lin_penalty=1.0, angular_penalty=1.0/360.0)
#print polygon_area(polygon=P)/r
#print compute_num_contours(polygon=P, radius=r)