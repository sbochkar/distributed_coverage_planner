"""Algorithm for pairwise reoptimization."""
import logging
from typing import List, Tuple, Optional
import sys

from shapely.geometry import LineString, Polygon, Point

from numpy import linspace
from itertools import product

from chi import compute_chi
from polygon_split import polygon_split


RADIUS = 0.1
LINEAR_PENALTY = 1        # Weights for the cost function
ANGULAR_PENALTY = 10    # Weights for the cost function


# Configure logging properties for this module
logger = logging.getLogger("pairwiseReoptimization")
fileHandler = logging.FileHandler("logs/pairwiseReoptimization.log")
streamHandler = logging.StreamHandler()
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)
logger.setLevel(logging.INFO)


def poly_shapely_to_canonical(polygon=[]):
    """
    A simple helper function to convert a shapely object representing a polygon
    intop a cononical form polygon.

    Args:
        polygon: A shapely object representing a polygon

    Returns:
        A polygon in canonical form.
    """

    if not polygon:
        return []

    canonicalPolygon = []

    if polygon.exterior.is_ccw:
        poly_exterior = list(polygon.exterior.coords)
    else:
        poly_exterior = list(polygon.exterior.coords)[::-1]


    holes = []
    for hole in polygon.interiors:
        if hole.is_ccw:
            holes.append(list(polygon.exterior.coords)[::-1])
        else:
            holes.append(list(polygon.exterior.coords))

    canonicalPolygon.append(poly_exterior)
    canonicalPolygon.append(holes)

    return canonicalPolygon


def compute_pairwise_optimal(polygon_a: Polygon,
                             polygon_b: Polygon,
                             robot_a_init_pos: Point,
                             robot_b_init_pos: Point,
                             num_samples: int = 100,
                             radius: float = 0.1,
                             lin_penalty: float = 1.0,
                             ang_penalty: float = 10*1.0/360) -> Optional[Tuple[Polygon]]:
    """
    Takes two adjacent polygons and attempts to modify the shared edge such that
    the metric chi is reduced.

    The actual algorithm:
        1. Combine the two polygons
        2. Find one cut that works better
        3. Return that cut or no cut if nothing better was found

    TODO:
        Need to investigate assignment of cells to robots.

    Args:
        polygon_a: First polygon in canonical form.
        polygon_b: Second polygoni n canonical form.
        robot_a_init_pos: Location of robot A.
        robot_b_init_pos: Location of robot B.
        num_samples: Samppling density to be used in the search for optimal cut.

    Returns:
        Returns the cut that minimizes the maximum chi metrix. Or None if no such
        cut exists or original cut is the best.
    """

    if not polygon_a or not polygon_b:
        logger.warning("Pairwise reoptimization is requested on an empty polygon.")
        return None

    if not robot_a_init_pos or not robot_b_init_pos:
        logger.warning("Pairwise reoptimization is requested on an empty init pos.")
        return None

    if not polygon_a.is_valid or not polygon_b.is_valid:
        logger.warning("Pariwise reoptimization is requested on invalid polygons.")
        return None

    if not polygon_a.is_valid or not polygon_b.is_valid:
        logger.warning("Pariwise reoptimization is requested on invalid polygons.")
        return None

    if not polygon_a.is_simple or not polygon_b.is_simple:
        logger.warning("Pariwise reoptimization is requested on nonsimple polygons.")
        return None

    if not polygon_a.touches(polygon_b):
        logger.warning("Pariwise reoptimization is requested on nontouching polys.")
        return None

    intersection = polygon_a.intersection(polygon_b)

    if not isinstance(intersection, LineString):
        logger.warning("Pariwise reoptimization is requested but they don't touch"
                       "at an edge.")
        return None

    # Combine the two polygons
    polygon_union = polygon_a.union(polygon_b)

    if not polygon_union.is_valid or not polygon_union.is_simple:
        logger.warning("Pariwise reoptimization is requested but the union resulted"
                       "in bad polygon.")
        return None

    if not isinstance(polygon_union, Polygon):
        logger.warning("Pariwise reoptimization is requested but union resulted in"
                       "non polygon.")
        return None

    # This search for better cut is over any two pairs of samples points on the exterior.
    # The number of points along the exterior is controlled by num_samples.
    search_space: List[Tuple] = []
    poly_exterior = polygon_union.exterior
    for distance in linspace(0, poly_exterior.length, num_samples):
        solution_candidate = poly_exterior.interpolate(distance)
        search_space.append((solution_candidate.x, solution_candidate.y))

    # Record the costs at this point
    chi_1 = compute_chi(polygon=polygon_a,
                        init_pos=robot_a_init_pos,
                        radius=radius,
                        lin_penalty=lin_penalty,
                        ang_penalty=ang_penalty)
    chi_2 = compute_chi(polygon=polygon_b,
                        init_pos=robot_b_init_pos,
                        radius=radius,
                        lin_penalty=lin_penalty,
                        ang_penalty=ang_penalty)

    init_max_chi = max(chi_1, chi_2)

    min_max_chi_final = sys.float_info.max
    min_candidate: Tuple[Tuple]

    for cut_edge in product(search_space, repeat=2):
        logger.debug("Cut candidate: %s", cut_edge)

        poly_split = polygon_split(polygon_union, LineString(cut_edge))

        if poly_split:
            logger.debug("%s Split Line: %s", 'GOOD', cut_edge)
        else:
            logger.debug("%s Split Line: %s", "BAD ", cut_edge)

        if poly_split:
            # Resolve cell-robot assignments here.
            # This is to avoid the issue of cell assignments that
            # don't make any sense after polygon cut.
            chi_a0 = compute_chi(polygon=poly_split[0],
                                 init_pos=Point(robot_a_init_pos),
                                 radius=radius,
                                 lin_penalty=lin_penalty,
                                 ang_penalty=ang_penalty)
            chi_a1 = compute_chi(polygon=poly_split[1],
                                 init_pos=Point(robot_a_init_pos),
                                 radius=radius,
                                 lin_penalty=lin_penalty,
                                 ang_penalty=ang_penalty)
            chi_b0 = compute_chi(polygon=poly_split[0],
                                 init_pos=Point(robot_b_init_pos),
                                 radius=radius,
                                 lin_penalty=lin_penalty,
                                 ang_penalty=ang_penalty)
            chi_b1 = compute_chi(polygon=poly_split[1],
                                 init_pos=Point(robot_b_init_pos),
                                 radius=radius,
                                 lin_penalty=lin_penalty,
                                 ang_penalty=ang_penalty)

            max_chi_cases = [max(chi_a0, chi_b1),
                             max(chi_a1, chi_b0)]

            min_max_chi = min(max_chi_cases)
            if min_max_chi <= min_max_chi_final:
                min_candidate = cut_edge
                min_max_chi_final = min_max_chi

    logger.debug("Computed min max chi as: %4.2f", min_max_chi_final)
    logger.debug("Cut: %s", min_candidate)

    if init_max_chi < min_max_chi_final:
        logger.debug("No cut results in minimum altitude")

        return None

    new_polygons = polygon_split(polygon_union, LineString(min_candidate))
    return new_polygons


if __name__ == '__main__':

    P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
    P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
    init_a = Point((0, 0))
    init_b = Point((1, 0))
    result = "PASS" if not compute_pairwise_optimal(P1, P2, init_a, init_b) else "FAIL"
    print("[%s] Simple two polygon test."%result)

    P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
    P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
    init_a = Point((0, 0))
    init_b = Point((0, 0))
    print(compute_pairwise_optimal(P1, P2, init_a, init_b))

    P1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [])
    P2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], [])
    init_a = Point((0, 0))
    init_b = Point((0, 1))
    print(compute_pairwise_optimal(P1, P2, init_a, init_b))
