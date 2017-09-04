from math import atan2
from math import pi


def get_directions_set(polygon=[]):
	"""Generates a list of directions orthogonal to edges of polygon

	[TODO]: Efficiency could be improved by removing duplicate directions

	Augs:
		polygon: a polygon in standard form
	Returns:
		directions: set of directions [rad]
	"""

	ext = P[0]
	holes = P[1]
	directions = []

	n = len(ext)
	for i in range(n):
		ax, ay = ext[i]
		bx, by = ext[(i+1)%n]

		directions.append(atan2(by-ay, bx-ax)+pi/2)


	for hole in holes:
		n = len(hole)
		for i in range(n):
			edge = [hole[i], hole[(i+1)%n]]
			ax, ay = edge[0]
			bx, by = edge[1]

			directions.append(atan2(by-ay, bx-ax)+pi/2)

	return directions