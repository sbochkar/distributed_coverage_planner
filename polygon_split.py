import logging

from shapely.geometry import Point
from shapely.geometry import MultiPoint
from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import LinearRing


# Configure logging properties for this module
logger = logging.getLogger("polygonSplit")
fileHandler = logging.FileHandler("logs/polygonSplit.log")
streamHandler = logging.StreamHandler()
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)
logger.setLevel(logging.INFO)


def pretty_print_poly(P=[]):
	"""Pretty prints cannonical polygons to help with debugging

	Args:
		P: Polygon in canonical form.

	Returns:
		None
	"""

	print("Polygon:\n\tExterior:\n\t\t"),

	for pts in P[0]:
		# Need to make sure to round some pts for nice display
		print("(%3.1f, %3.1f), "%(pts[0], pts[1])),
	print("")
	holeCnt = 0
	for hole in P[1]:
		print("\tHole %d:\n\t\t"%holeCnt),
		for pts in hole:
			# Need to make sure to round some pts for nice display
			print("(%3.1f, %3.1f),"%(pts[0], pts[1])),
		print("")
		holeCnt += 1


def convert_to_canonical(P=[]):
	"""Convertion function to convert from shapely object to canonical form.

	Args:
		P: Shapely object representing a polygon.

	Returns:
		poly: A polygon represented in canonical form. [] otherwise.
	"""

	if type(P) is not Polygon:
		logger.warn("Polygon conversion requested but wrong input specified.")
		return []

	poly = [[], []]

	if not LinearRing(P.exterior.coords).is_ccw:
		poly[0] = list(P.exterior.coords)[::-1][:-1]
	else:
		poly[0] = list(P.exterior.coords)[:-1]

	for hole in P.interiors:

		if LinearRing(hole.coords).is_ccw:
			poly[1].append(list(hole.coords)[::-1][:-1])
		else:
			poly[1].append(list(hole.coords)[:-1])

	return poly


def polygon_split(polygon=[], splitLine=[]):
	"""Split a polygon into two other polygons along splitLine.

	Attempts to split a polygon into two other polygons. Here, a number of
	assumptions has to be made. That is, that splitLine is a proper line
	connecting 	boundaries of a polygon. Also, that splitLine does not connect
	outside boundary to a boundary of hole. This is a undefined behaviour.

	TODO: With current implementation, it may be possible to do non-decomposing
		cuts. But, some thought needs to be put in.

	@startuml

	(*) --> "Check Inputs"
	if "OK?" then
		-->[true] "Intersection boundary with cut"
		if "Outputs OK?" then
			--> "Difference boundary with cut"
			if "Outputs OK?" then
				-->[true] ===Chunks=== 
				--> "Form masking polygon"
				--> "Intersect masking polygon with input polygon"
				===Chunks=== --> "Form masking polygon 2"
				--> "Intersect masking polygon with input polygon"
				if "Output OK?" then
					-->[true] Return both polygons
				else
					-->[false] (*)
				endif
			else
				-->[false] (*)
			endif

		else
			-->[false] (*)
		endif
		


	else
	    -->[false] (*)
	endif

	@enduml

	Args:
		polygon: Shapely polygon object.
		splitLine: Shapely LineString object.

	Returns:
		(P1, P2): A tuple of Shapely polygons resulted from the split. If error occured,
		returns [].

	"""

	if not splitLine or not polygon:
		return []

	if not polygon.is_valid:
		return []

	# This calculates the points on the boundary where the split will happen.
	extLine = polygon.exterior
	commonPts = extLine.intersection(splitLine)
	logger.debug("Cut: %s Intersection: %s"%(splitLine, commonPts))

	# No intersection check.
	if not commonPts:
		return []
	# This intersection should always have only 2 points.
	if type(commonPts) is not MultiPoint:
		return []
	# Should only ever contain two points.
	if len(commonPts) != 2:
		return []
	# Split line should be inside polygon.
	if not splitLine.within(polygon):
		return []
	# Check to see if cut line touches any holes
	for hole in polygon.interiors:
		if splitLine.intersects(hole):
			return []




	splitBoundary = extLine.difference(splitLine)
	# Check that splitBoundary is a collection of linestrings
	if type(splitBoundary) is not MultiLineString:
		return []
	# Make sure there are only 2 linestrings in the collection
 	if len(splitBoundary) > 3 or len(splitBoundary) < 2:
 		return []

	logger.debug("Split boundary: %s"%splitBoundary)

	# Even though we use LinearRing, there is no wrap around and diff produces
	#	3 strings. Need to union. Not sure if combining 1st and last strings 
	#	is guaranteed to be the right combo. For now, place a check.
	if len(splitBoundary) == 3:
		if splitBoundary[0].coords[0] != splitBoundary[-1].coords[-1]:
			logger.warn("The assumption that pts0[0] == pts2[-1] DOES not hold. Need"
					"to investigate.")
			return []

		line1 = LineString(list(list(splitBoundary[-1].coords)[:-1]+list(splitBoundary[0].coords)))
	else:
		line1 = splitBoundary[0]
	line2 = splitBoundary[1]


	if len(line1.coords) < 3 or len(line2.coords) < 3:
		return []

	mask1 = Polygon(line1)
	mask2 = Polygon(line2)

	if (not mask1.is_valid) or (not mask2.is_valid):
		return []

	resP1Pol = polygon.intersection(mask1)
	resP2Pol = polygon.intersection(mask2)

	if type(resP1Pol) is not Polygon:
		return []
	if type(resP2Pol) is not Polygon:
		return []
	if not resP1Pol.is_valid:
		return []
	if not resP2Pol.is_valid:
		return []

	return resP1Pol, resP2Pol


if __name__ == '__main__':


	P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [[(0.1, 0.1), (0.1, 0.9), (0.9, 0.9), (0.9, 0.1)]])
	e = LineString([(0.05, 0), (0.05, 1)])
	P1, P2 = polygon_split(P, e)

	P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
	e = LineString([(1, 0.8), (0.8, 1)])
	P1, P2 = polygon_split(P, e)

	P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
	e = LineString([(0.2, 1), (0, 0.8)])
	P1, P2 = polygon_split(P, e)

	P = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
	e = LineString([(0, 0.2), (0.2, 0)])
	P1, P2 = polygon_split(P, e)
	#pretty_print_poly(P1)
	#pretty_print_poly(P2)