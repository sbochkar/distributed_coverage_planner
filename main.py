"""Entry point for distributed planner"""
import sys

from utils.polygons import decomposition_generator
from utils import greedy_decomposition
from optimizer import ChiOptimizer
from log_utils import get_logger
import visuals.coverage_plot as splot


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
    # Start visuals
    # Initialize plotting tools
    ax_old = splot.init_axis("Original Decomposition", "+0+100")
    ax_new = splot.init_axis("Reoptimized Decomposition", "+700+100")


    #polygon, cell_to_site_map, decomposition = decomposition_generator(poly_id)
    decomposition = decomposition_generator(poly_id)
    splot.plot_polygon_outline(ax_old, decomposition.canonical_polygon)
    splot.plot_decomposition(ax_old, decomposition)
    splot.plot_init_pos_and_assignment(ax_old, decomposition)

    logger.info("Reoptimizing polygon: %3d", poly_id)
    logger.info("Attempting %d reoptimization iterations.", num_reopt_iters)

    optimizer = ChiOptimizer(num_iterations=num_reopt_iters,
                             radius=RADIUS,
                             lin_penalty=LINEAR_PENALTY,
                             ang_penalty=ANGULAR_PENALTY)
    old_costs, new_costs = optimizer.run_iterations(decomposition)

    # Populate the drawing canvas
    splot.plot_polygon_outline(ax_new, decomposition.canonical_polygon)
    splot.plot_decomposition(ax_new, decomposition)
    splot.plot_init_pos_and_assignment(ax_new, decomposition)

    logger.info("Old costs: %s", old_costs)
    logger.info("New costs: %s", new_costs)

    # Each cell is further decomposition for path planning purposes.
    for cell_id, polygon, site in decomposition.items():
        ax_cvx = splot.init_axis("Convex Decomposition", "+0+100")
        dec = greedy_decomposition(polygon)



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
