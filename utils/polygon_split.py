from typing import Optional, Tuple

from shapely.geometry import Point
from shapely.geometry import MultiPoint
from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import LinearRing

from log_utils import get_logger


# Configure logging properties for this module
logger = get_logger("polygon_split")


def polygon_split(polygon: Polygon, split_line: LineString) -> Optional[Tuple[Polygon, Polygon]]:
    """Split a polygon into two other polygons along split_line.

    Attempts to split a polygon into two other polygons. Here, a number of
    assumptions has to be made. That is, that split_line is a proper line
    connecting     boundaries of a polygon. Also, that split_line does not connect
    outside boundary to a boundary of hole. This is a undefined behaviour.

    TODO: With current implementation, it may be possible to do non-decomposing
        cuts. But, some thought needs to be put in.

    Assumptions:
        Input polygon and split_line are valid.

    Args:
        polygon: Shapely polygon object.
        split_line: Shapely LineString object.

    Returns:
        (P1, P2): A tuple of Shapely polygons resulted from the split. If error occured,
        returns [].

    """

    # This calculates the points on the boundary where the split will happen.
    ext_line = polygon.exterior
    common_pts = ext_line.intersection(split_line)
    logger.debug("Cut: %s Intersection: %s", split_line, common_pts)

    # No intersection check.
    if not common_pts:
        return None
    # This intersection should always have only 2 points.
    if not isinstance(common_pts, MultiPoint):
        return None
    # Should only ever contain two points.
    if len(common_pts) != 2:
        return None
    # Split line should be inside polygon.
    if not split_line.within(polygon):
        return None
    # Check to see if cut line touches any holes
    for hole in polygon.interiors:
        if split_line.intersects(hole):
            return None

    split_boundary = ext_line.difference(split_line)
    # Check that split_boundary is a collection of linestrings
    if not isinstance(split_boundary, MultiLineString):
        return None
    # Make sure there are only 2 linestrings in the collection
    if len(split_boundary) > 3 or len(split_boundary) < 2:
        return None

    logger.debug("Split boundary: %s", split_boundary)

    # Even though we use LinearRing, there is no wrap around and diff produces
    #    3 strings. Need to union. Not sure if combining 1st and last strings
    #    is guaranteed to be the right combo. For now, place a check.
    if len(split_boundary) == 3:
        if split_boundary[0].coords[0] != split_boundary[-1].coords[-1]:
            logger.warning("The assumption that pts0[0] == pts2[-1] DOES not hold. Need"
                           " to investigate.")
            return None

        line1 = LineString(
            list(list(split_boundary[-1].coords)[:-1] + list(split_boundary[0].coords)))
    else:
        line1 = split_boundary[0]
    line2 = split_boundary[1]


    if len(line1.coords) < 3 or len(line2.coords) < 3:
        return None

    mask1 = Polygon(line1)
    mask2 = Polygon(line2)

    if (not mask1.is_valid) or (not mask2.is_valid):
        return None

    res_p1_pol = polygon.intersection(mask1)
    res_p2_pol = polygon.intersection(mask2)

    if not isinstance(res_p1_pol, Polygon):
        return None
    if not isinstance(res_p2_pol, Polygon):
        return None
    if not res_p1_pol.is_valid:
        return None
    if not res_p2_pol.is_valid:
        return None

    return res_p1_pol, res_p2_pol


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
