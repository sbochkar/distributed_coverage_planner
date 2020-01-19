"""Entry point for distributed planner"""
from typing import List
import sys

import coverage_plot as splot

from polygons import decomposition_generator
from optimizer import ChiOptimizer
from log_utils import get_logger


GLKH_LOCATION = "/home//misc/GLKH-1.0/"

NUM_SAMPLES = 10
NUM_REOPT_ITERATIONS = 5
RADIUS = 0.2
LINEAR_PENALTY = 1.0
ANGULAR_PENALTY = 100*1.0/360
DEBUG_LEVEL = 0


logger = get_logger("main")


def pretty_print_decomposition(decomposition):
    """Pretty print for polygons."""
    print("[..] decompositionosition:")
    for idx, poly in enumerate(decomposition):
        print("%2d: "%idx),
        boundary = poly[0]
        for elem in boundary:
            print("(%.2f, %.2f), "%(elem[0],elem[1])),
        print("\n"),


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


def distributed_planner(poly_id: int = 0, num_reopt_iters: int = 10):
    """
    Main function that orchestrates distrubted planner and plots the results.

    Assumptions:
        Robots are assigned to the cells nearest to them.

    TODO:
        -

    Args:
        poly_id (int): Id of the polygon. Needed to select started polygons.
        num_reopt_iters (int): Run reoptimizer for this many iterations.
    """
    polygon, cell_to_site_map, decomposition = decomposition_generator(poly_id)

    old_costs: List[float] = []
    new_costs: List[float] = []

    logger.info("Reoptimizing polygon: %3d", poly_id)
    logger.info("Attempting %d reoptimization iterations.", num_reopt_iters)
    optimizer = ChiOptimizer(num_iterations=num_reopt_iters,
                             radius=RADIUS,
                             lin_penalty=LINEAR_PENALTY,
                             ang_penalty=ANGULAR_PENALTY)
    new_decomposition = optimizer.run_iterations(decomposition,
                                                 cell_to_site_map,
                                                 old_costs,
                                                 new_costs)

    # TODO: Temporary w.a. until we completely transition to Polygon objects.
    new_decomposition = [poly_shapely_to_canonical(poly) for poly in new_decomposition]

    print("Old costs: %s"%old_costs)
    print("New costs: %s"%new_costs)


    # For this step, need to implement minimum altitude decomposition
    # For now, just plan a path for each robot
    #min_alt_decomposition = []
    #for polygon in new_decomposition:

        #from reflex import find_reflex_vertices
        #reflex_verts = reflex.find_reflex_vertices(P)
        #compute_min_alt_cut(polygon, reflex_vertex)
        #min_alt_decomposition.append(min_alt(polygon))



    # Start visuals
    # Initialize plotting tools
    ax_old = splot.init_axis("Original Decomposition", "+0+100")
    ax_new = splot.init_axis("Reoptimized Decomposition", "+700+100")

    # Populate the drawing canvas
    splot.plot_polygon_outline(ax_old, polygon)
    splot.plot_polygon_outline(ax_new, polygon)

    splot.plot_decomposition(ax_old, decomposition)
    splot.plot_decomposition(ax_new, new_decomposition)

    splot.plot_init_pos_and_assignment(ax_old, cell_to_site_map, decomposition)
    splot.plot_init_pos_and_assignment(ax_new, cell_to_site_map, decomposition)

    # Send the plot command
    splot.display()





#segments = discrt.discritize_set(decomposition, radius)
#mapping = get_mapping.get_mapping(segments)
#cost_matrix, cluster_list = dubins_cost.compute_costs(orig_poly, mapping, radius/2)
#solver.solve("cpp_test", GLKH_LOCATION, cost_matrix, cluster_list)
#tour = solver.read_tour("cpp_test")
#print cell_to_site_map

#single_planner.single_planner(decomposition, radius, orig_poly, cell_to_site_map)

#Initialize plotting tools



#splot.plot_samples(ax, segments)
#splot.plot_tour_dubins(ax, tour, mapping, RADIUS/2)
#splot.display()

if __name__ == '__main__':

    poly_id_ = int(sys.argv[1])

    distributed_planner(poly_id=poly_id_)
