from math import cos
from math import sin


def rotate_points(vertices, theta):
	"""Rotate a set of vertices by theta

	Rotate a list of vertices consisting of (x,y) tuples by applygin rigid
	transformation. Preserves the order of verticies.

	Args:
		vertices: List of (x, y) coordinates
		theta: Angle of rotation

	Returns:
		rotatedVerts: List of new points
	"""

	global DEBUG_LEVEL

	n = len(vertices)
	if not n:
		if DEBUG_LEVEL & 0x04:
			print("Rotation requested on empty input.")
		return []

	cosTh = cos(theta)
	sinTh = sin(theta)

	rotatedVerts = []
	for i in range(n):
		xNew = vertices[i][0]*cosTh - vertices[i][1]*sinTh
		yNew = vertices[i][0]*sinTh + vertices[i][1]*cosTh

		rotatedVerts.append( (xNew, yNew) )

	return rotatedVerts


def rotate_polygon(P, theta):
	"""
	Rotate a polygon

	Rotate a polygon in standard form by applygin rigid
	transformation

	Args:
		P: Polygon in standard form
		theta: the angle of rotation

	Returns:
		polygon: rotated polygon
	"""

	cos_th = cos(theta)
	sin_th = sin(theta)

	n = len(P[0])
	if not n:
		print "rotate: polygon list EMPTY!"
		return None

	ext = []
	for i in range(n):
		x_new = P[0][i][0]*cos_th-P[0][i][1]*sin_th
		y_new = P[0][i][0]*sin_th+P[0][i][1]*cos_th

		ext.append( (x_new, y_new) )

	holes = []
	for hole in P[1]:
		new_hole = []
		for i in range(len(hole)):
			x_new = hole[i][0]*cos_th-hole[i][1]*sin_th
			y_new = hole[i][0]*sin_th+hole[i][1]*cos_th

			new_hole.append((x_new, y_new))
		holes.append(new_hole)


	return [ext, holes]