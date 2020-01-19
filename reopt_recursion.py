"""Algorithm for recursive reoptimization of polygon."""
import logging
from typing import Dict, List
from numpy import linspace

from shapely.geometry import LineString, Polygon, Point

from chi import compute_chi
from pairwise_reopt import compute_pairwise_optimal
from decomposition_processing import compute_adjacency


# Need to move these to the main calling function
RADIUS = 0.2
LINEAR_PENALTY = 1.0
ANGULAR_PENALTY = 10*1.0/360


# Configure logging properties for this module
logger = logging.getLogger("recursive_reoptimizer")
fileHandler = logging.FileHandler("logs/recursive_reoptimizer.log")
streamHandler = logging.StreamHandler()
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)


def dft_recursion(decomposition,
                  adjacency_matrix,
                  max_vertex_idx: int,
                  cell_to_site_map: Dict,
                  radius: float = 0.1,
                  lin_penalty: float = 1.0,
                  ang_penalty: float = 10*1.0/360):
    """
    This is a recursive function that explores all pairs of cells starting with
    one with the highest cost. The purpose is to re-optimize cuts of adjacent
    cells such that the maximum cost over all cells in the map is minimized.

    Assumption:
        The adjacency value for a cell with iteself should be None

    Params:
        decomposition: A decomposition as a list of polygons.
        adjacency_matrix: A matrix representing adjacency relationships between
                         cells in the decomposition.
        max_vertex_idx: Index of a cell in the decomposition with the maximum cost.

    Returns:
        True if a succseful reoptimization was performed. False otherwise.
    """

    max_vertex_cost = compute_chi(polygon=decomposition[max_vertex_idx],
                                  init_pos=cell_to_site_map[max_vertex_idx],
                                  radius=radius,
                                  lin_penalty=lin_penalty,
                                  ang_penalty=ang_penalty)

    logger.debug("Cell %d has maximum cost of : %f", max_vertex_idx, max_vertex_cost)

    surrounding_cell_idxs = []
    for cell_idx, is_adjacent in enumerate(adjacency_matrix[max_vertex_idx]):
        if is_adjacent:
            surrounding_cell_idxs.append(cell_idx)

    logger.debug("Surrounding Cell Idxs: %s", surrounding_cell_idxs)

    surrounding_chi_costs = []
    for cell_idx in surrounding_cell_idxs:
        cost = compute_chi(polygon=decomposition[cell_idx],
                           init_pos=cell_to_site_map[cell_idx],
                           radius=radius,
                           lin_penalty=lin_penalty,
                           ang_penalty=ang_penalty)
        surrounding_chi_costs.append((cell_idx, cost))


    sorted_surrounding_chi_costs = sorted(surrounding_chi_costs,
                                          key=lambda v: v[1],
                                          reverse=False)
    logger.debug("Neghbours and chi: %s", sorted_surrounding_chi_costs)

    # Idea: For a given cell with maximum cost, search all the neighbors
    #        and sort them based on their chi cost.
    #
    #        Starting with the neighbor with the lowest cost, attempt to
    #        reoptimize the cut seperating them in hopes of minimizing the max
    #        chi of the two cells.
    #
    #        If the reoptimization was succesful then stop recursion and complete
    #        the iteration.
    #
    #        If the reoptimization was not succesful then it is possible that we
    #        are in a local minimum and we need to disturb the search in hopes
    #        of finiding a better solution.
    #
    #        For that purpose, we call the recursive function on the that
    #        neighboring cell. And so on.
    #
    #        If the recursive function for that neighboring cell does not yield
    #        a reoptimization then we pick the next lowest neighbor and attempt
    #        recursive reoptimization. This ensures DFT of the adjacency graph.

    for cell_idx, cell_chi_cost in sorted_surrounding_chi_costs:

        if cell_chi_cost < max_vertex_cost:
            logger.debug("Attempting reopt %d and %d.", max_vertex_idx, cell_idx)

            result = compute_pairwise_optimal(polygon_a=decomposition[max_vertex_idx],
                                              polygon_b=decomposition[cell_idx],
                                              robot_a_init_pos=cell_to_site_map[max_vertex_idx],
                                              robot_b_init_pos=cell_to_site_map[cell_idx],
                                              num_samples=50,
                                              radius=radius,
                                              lin_penalty=lin_penalty,
                                              ang_penalty=ang_penalty)

            if result:
                # Resolve cell-robot assignments here.
                # This is to avoid the issue of cell assignments that
                # don't make any sense after polygon cut.
                chi_a0 = compute_chi(polygon=result[0],
                                     init_pos=cell_to_site_map[max_vertex_idx],
                                     radius=radius,
                                     lin_penalty=lin_penalty,
                                     ang_penalty=ang_penalty)
                chi_a1 = compute_chi(polygon=result[1],
                                     init_pos=cell_to_site_map[max_vertex_idx],
                                     radius=radius,
                                     lin_penalty=lin_penalty,
                                     ang_penalty=ang_penalty)
                chi_b0 = compute_chi(polygon=result[0],
                                     init_pos=cell_to_site_map[cell_idx],
                                     radius=radius,
                                     lin_penalty=lin_penalty,
                                     ang_penalty=ang_penalty)
                chi_b1 = compute_chi(polygon=result[1],
                                     init_pos=cell_to_site_map[cell_idx],
                                     radius=radius,
                                     lin_penalty=lin_penalty,
                                     ang_penalty=ang_penalty)

                if max(chi_a0, chi_b1) <= max(chi_a1, chi_b0):
                    decomposition[max_vertex_idx], decomposition[cell_idx] = result
                else:
                    decomposition[cell_idx], decomposition[max_vertex_idx] = result

                logger.debug("Cells %d and %d reopted.", max_vertex_idx, cell_idx)

                adjacency_matrix = compute_adjacency(decomposition)

                return True

            if dft_recursion(decomposition=decomposition,
                             adjacency_matrix=adjacency_matrix,
                             max_vertex_idx=cell_idx,
                             cell_to_site_map=cell_to_site_map,
                             radius=radius,
                             lin_penalty=lin_penalty,
                             ang_penalty=ang_penalty):
                return True
    return False


if __name__ == '__main__':

    # If package is launched from cmd line, run sanity checks
    #global DEBUG_LEVEL

    DEBUG_LEVEL = 0 #0x8+0x4

    print("\nSanity tests for recursive reoptimization.\n")


    P = [[(0.0,0.0),(10.0,0.0),(10.0,1.0),(0.0,1.0)],[]]
    q = [(0.0,0.0),(10.0,0.0),(10.0,1.0),(0.0,1.0)]
    decomposition = [[[(0.0,0.0),(2.5,0.0),(2.5,1.0),(0.0,1.0)],[]], [[(2.5,0.0),(5.0,0.0),(5.0,1.0),(2.5,1.0)],[]], [[(5.0,0.0),(7.5,0.0),(7.5,1.0),(5.0,1.0)],[]], [[(7.5,0.0),(10.0,0.0),(10.0,1.0),(7.5,1.0)],[]]]
    adjMatrix = [[False, True, False, False], [True, False, True, False], [False, True, False, True], [False, False, True, False]]
    cell_to_site_map = {0: (10,0), 1:(10,1), 2:(0,1), 3:(0,0)}
    print(dft_recursion(decomposition, adjMatrix, 3, cell_to_site_map))
    print(decomposition)
    #result = "PASS" if not dft_recursion(P1, P2, initA, initB) else "FAIL"
    #print("[%s] Simple two polygon test."%result)
