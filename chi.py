import logging
from math import sqrt

from shapely.geometry import LinearRing
from shapely.geometry import LineString
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon


# Configure logging properties for this module
logger = logging.getLogger("chi")
fileHandler = logging.FileHandler("chi.log")
streamHandler = logging.StreamHandler()
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)


def compute_num_contours(polygon=[], radius=1):
	"""
	Computing contours of P

	Params:
		polygon: A shapely object representing the polygon
		solverParams: A dict representing solver parameters
	Returns:
		Number of contours
	"""

	level = 0
	num_contours = 0

	test_polygon = Polygon(polygon).buffer(-(2*level+1)*radius/2.0)

	while not test_polygon.is_empty:
		test_polygon = test_polygon.buffer(-(2*level+1)*radius/2.0)
		level += 1		

		if type(test_polygon) is MultiPolygon:
			num_contours += len(test_polygon)
		else:
			num_contours += 1

	logger.debug("Number of contours: %d"%num_contours)

	return num_contours


def compute_chi(polygon=[], initPos=[], radius=1, linPenalty=1.0, angPenalty=1.0):
	"""
	Metric chi: Approximation of the cost of a coverage path for a polygon

	F1: distance from robot to the polygon and back
	F2: sum of lengths of straight line segments
	F3: approximation of the angular component of polygon

	Args:
		polygon: A shapely object representing the polygon
		initPos: A shapely point  representing Initial position of the robot
		solverParams: A dict containing solver settings
	Returns:
		chi: Cost chi of coverage of the polygon
	"""

	K1 = 2.0
	K2 = 1.0/radius
	K3 = 360.0

	F1 = K1*polygon.distance(initPos)
	F2 = K2*polygon.area
	F3 = K3*compute_num_contours(polygon=polygon, radius=radius)

	logger.debug("F1: %6.2f F2: %6.2f F3: %6.2f"%(F1, F2, F3))

	return linPenalty*(F1 + F2) + angPenalty*F3


if __name__ == "__main__":

	from shapely.geometry import Polygon
	from shapely.geometry import Point

	P = Polygon([(00, 0), (1, 0), (1, 1), (0, 1)])
	p = Point((0,0))
	compute_chi(P, p, 1, 1, 1)


#P = [[(0,0),(1,0),(1,1),(0,1)],[]]
#P = [[(0,0),(4,0),(4,1),(6,1),(6,0),(10,0),(10,3),(6,3),(6,2),(4,2),(4,3),(0,3)],[]]
#q = (-1,-1)
#r = 0.5

#print chi(polygon=P, initPos=q, radius=r, lin_penalty=1.0, angular_penalty=1.0/360.0)
#print polygon_area(polygon=P)/r
#print compute_num_contours(polygon=P, radius=0.1)