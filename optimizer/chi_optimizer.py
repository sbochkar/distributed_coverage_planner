"""High level optimizer that runs iterations."""
from itertools import product
from typing import Dict, List, Tuple, Optional
import sys

from numpy import linspace
from shapely.geometry import LineString, Polygon, Point

from log_utils import get_logger
from decomposition_processing import compute_adjacency
from chi import compute_chi
from polygon_split import polygon_split


class ChiOptimizer():
    """Main functionality of the optimizer."""
    __slots__ = (
        'num_iterations',
        'radius',
        'lin_penalty',
        'ang_penalty',
        'logger',
    )

    def __init__(self,
                 num_iterations: int = 10,
                 radius: float = 0.1,
                 lin_penalty: float = 1.0,
                 ang_penalty: float = 10 * 1.0 / 360.):
        self.num_iterations = num_iterations
        self.radius = radius
        self.lin_penalty = lin_penalty
        self.ang_penalty = ang_penalty
        self.logger = get_logger(self.__class__.__name__)

    def run_iterations(self,
                       decomposition: List[Polygon],
                       cell_to_site_map: Dict[int, Point]) -> Tuple[List[Polygon],
                                                                    List[Tuple[int, float]],
                                                                    List[Tuple[int, float]]]:
        """
        Performs pairwise reoptimization on the poylgon with given robot initial
        position.

        Args:
            decomposition: A set of polygon representing the decomposition.
            cell_to_site_map: A mapping between robot and starting location.
        Returns:
            New decomposition
            List of original costs
            List of new chi costs
        """
        original_chi_costs: List[Tuple[int, float]] = []

        for i in range(self.num_iterations):

            # TODO: Really, chi_costs should be a map.
            chi_costs: List[Tuple[int, float]] = []
            for idx, poly in enumerate(decomposition):
                cost = compute_chi(polygon=poly,
                                   init_pos=cell_to_site_map[idx],
                                   radius=self.radius,
                                   lin_penalty=self.lin_penalty,
                                   ang_penalty=self.ang_penalty)
                chi_costs.append((idx, cost))
            sorted_chi_costs = sorted(chi_costs, key=lambda v: v[1], reverse=True)

            if not original_chi_costs:
                # Store orignal stats for monitoring performance of the algorithm.
                original_chi_costs = list(sorted_chi_costs)

            self.logger.debug("Iteration: %3d/%3d: Costs: %s", i, self.num_iterations,
                              sorted_chi_costs)

            adjacency_matrix = compute_adjacency(decomposition)

            if not self.dft_recursion(decomposition,
                                      adjacency_matrix,
                                      sorted_chi_costs[0][0],
                                      cell_to_site_map):
                self.logger.debug("Iteration: %3d/%3d: No cut was made!", i, self.num_iterations)

            self.logger.debug("[%3d]: %s\n", i + 1, sorted_chi_costs)

        chi_costs_: List[Tuple[int, float]] = []
        for idx, poly in enumerate(decomposition):
            cost = compute_chi(polygon=poly,
                               init_pos=cell_to_site_map[idx],
                               radius=self.radius,
                               lin_penalty=self.lin_penalty,
                               ang_penalty=self.ang_penalty)
            chi_costs_.append((idx, cost))
        sorted_chi_costs = sorted(chi_costs, key=lambda v: v[1], reverse=True)
        new_chi_costs = list(sorted_chi_costs)

        self.logger.debug("[%3d]: %s\n", i + 1, sorted_chi_costs)

        return decomposition, original_chi_costs, new_chi_costs

    def dft_recursion(self,
                      decomposition: List[Polygon],
                      adjacency_matrix,
                      max_vertex_idx: int,
                      cell_to_site_map: Dict[int, Point]):
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
                                      radius=self.radius,
                                      lin_penalty=self.lin_penalty,
                                      ang_penalty=self.ang_penalty)

        self.logger.debug("Cell %d has maximum cost of : %f", max_vertex_idx, max_vertex_cost)

        surrounding_cell_idxs = []
        for cell_idx, is_adjacent in enumerate(adjacency_matrix[max_vertex_idx]):
            if is_adjacent:
                surrounding_cell_idxs.append(cell_idx)

        self.logger.debug("Surrounding Cell Idxs: %s", surrounding_cell_idxs)

        surrounding_chi_costs = []
        for cell_idx in surrounding_cell_idxs:
            cost = compute_chi(polygon=decomposition[cell_idx],
                               init_pos=cell_to_site_map[cell_idx],
                               radius=self.radius,
                               lin_penalty=self.lin_penalty,
                               ang_penalty=self.ang_penalty)
            surrounding_chi_costs.append((cell_idx, cost))

        sorted_surrounding_chi_costs = sorted(surrounding_chi_costs,
                                              key=lambda v: v[1],
                                              reverse=False)
        self.logger.debug("Neghbours and chi: %s", sorted_surrounding_chi_costs)

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
                self.logger.debug("Attempting reopt %d and %d.", max_vertex_idx, cell_idx)

                result = self.compute_pairwise_optimal(polygon_a=decomposition[max_vertex_idx],
                                                       polygon_b=decomposition[cell_idx],
                                                       robot_a_init_pos=cell_to_site_map[max_vertex_idx],
                                                       robot_b_init_pos=cell_to_site_map[cell_idx],
                                                       num_samples=50)

                if result:
                    # Resolve cell-robot assignments here.
                    # This is to avoid the issue of cell assignments that
                    # don't make any sense after polygon cut.
                    chi_a0 = compute_chi(polygon=result[0],
                                         init_pos=cell_to_site_map[max_vertex_idx],
                                         radius=self.radius,
                                         lin_penalty=self.lin_penalty,
                                         ang_penalty=self.ang_penalty)
                    chi_a1 = compute_chi(polygon=result[1],
                                         init_pos=cell_to_site_map[max_vertex_idx],
                                         radius=self.radius,
                                         lin_penalty=self.lin_penalty,
                                         ang_penalty=self.ang_penalty)
                    chi_b0 = compute_chi(polygon=result[0],
                                         init_pos=cell_to_site_map[cell_idx],
                                         radius=self.radius,
                                         lin_penalty=self.lin_penalty,
                                         ang_penalty=self.ang_penalty)
                    chi_b1 = compute_chi(polygon=result[1],
                                         init_pos=cell_to_site_map[cell_idx],
                                         radius=self.radius,
                                         lin_penalty=self.lin_penalty,
                                         ang_penalty=self.ang_penalty)

                    if max(chi_a0, chi_b1) <= max(chi_a1, chi_b0):
                        decomposition[max_vertex_idx], decomposition[cell_idx] = result
                    else:
                        decomposition[cell_idx], decomposition[max_vertex_idx] = result

                    self.logger.debug("Cells %d and %d reopted.", max_vertex_idx, cell_idx)

                    adjacency_matrix = compute_adjacency(decomposition)

                    return True

                if self.dft_recursion(decomposition=decomposition,
                                      adjacency_matrix=adjacency_matrix,
                                      max_vertex_idx=cell_idx,
                                      cell_to_site_map=cell_to_site_map):
                    return True
        return False

    def compute_pairwise_optimal(self,
                                 polygon_a: Polygon,
                                 polygon_b: Polygon,
                                 robot_a_init_pos: Point,
                                 robot_b_init_pos: Point,
                                 num_samples: int = 100) -> Optional[Tuple[Polygon]]:
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
            self.logger.warning("Pairwise reoptimization is requested on an empty polygon.")
            return None

        if not robot_a_init_pos or not robot_b_init_pos:
            self.logger.warning("Pairwise reoptimization is requested on an empty init pos.")
            return None

        if not polygon_a.is_valid or not polygon_b.is_valid:
            self.logger.warning("Pariwise reoptimization is requested on invalid polygons.")
            return None

        if not polygon_a.is_valid or not polygon_b.is_valid:
            self.logger.warning("Pariwise reoptimization is requested on invalid polygons.")
            return None

        if not polygon_a.is_simple or not polygon_b.is_simple:
            self.logger.warning("Pariwise reoptimization is requested on nonsimple polygons.")
            return None

        if not polygon_a.touches(polygon_b):
            self.logger.warning("Pariwise reoptimization is requested on nontouching polys.")
            return None

        intersection = polygon_a.intersection(polygon_b)

        if not isinstance(intersection, LineString):
            self.logger.warning("Pariwise reoptimization is requested but they don't touch"
                                " at an edge.")
            return None

        # Combine the two polygons
        polygon_union = polygon_a.union(polygon_b)

        if not polygon_union.is_valid or not polygon_union.is_simple:
            self.logger.warning("Pariwise reoptimization is requested but the union resulted"
                                " in bad polygon.")
            return None

        if not isinstance(polygon_union, Polygon):
            self.logger.warning("Pariwise reoptimization is requested but union resulted in"
                                " non polygon.")
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
                            radius=self.radius,
                            lin_penalty=self.lin_penalty,
                            ang_penalty=self.ang_penalty)
        chi_2 = compute_chi(polygon=polygon_b,
                            init_pos=robot_b_init_pos,
                            radius=self.radius,
                            lin_penalty=self.lin_penalty,
                            ang_penalty=self.ang_penalty)

        init_max_chi = max(chi_1, chi_2)

        min_max_chi_final = sys.float_info.max
        min_candidate: Tuple[Tuple]

        for cut_edge in product(search_space, repeat=2):
            self.logger.debug("Cut candidate: %s", cut_edge)

            poly_split = polygon_split(polygon_union, LineString(cut_edge))

            if poly_split:
                self.logger.debug("%s Split Line: %s", 'GOOD', cut_edge)
            else:
                self.logger.debug("%s Split Line: %s", "BAD ", cut_edge)

            if poly_split:
                # Resolve cell-robot assignments here.
                # This is to avoid the issue of cell assignments that
                # don't make any sense after polygon cut.
                chi_a0 = compute_chi(polygon=poly_split[0],
                                     init_pos=Point(robot_a_init_pos),
                                     radius=self.radius,
                                     lin_penalty=self.lin_penalty,
                                     ang_penalty=self.ang_penalty)
                chi_a1 = compute_chi(polygon=poly_split[1],
                                     init_pos=Point(robot_a_init_pos),
                                     radius=self.radius,
                                     lin_penalty=self.lin_penalty,
                                     ang_penalty=self.ang_penalty)
                chi_b0 = compute_chi(polygon=poly_split[0],
                                     init_pos=Point(robot_b_init_pos),
                                     radius=self.radius,
                                     lin_penalty=self.lin_penalty,
                                     ang_penalty=self.ang_penalty)
                chi_b1 = compute_chi(polygon=poly_split[1],
                                     init_pos=Point(robot_b_init_pos),
                                     radius=self.radius,
                                     lin_penalty=self.lin_penalty,
                                     ang_penalty=self.ang_penalty)

                max_chi_cases = [max(chi_a0, chi_b1),
                                 max(chi_a1, chi_b0)]

                min_max_chi = min(max_chi_cases)
                if min_max_chi <= min_max_chi_final:
                    min_candidate = cut_edge
                    min_max_chi_final = min_max_chi

        self.logger.debug("Computed min max chi as: %4.2f", min_max_chi_final)
        self.logger.debug("Cut: %s", min_candidate)

        if init_max_chi < min_max_chi_final:
            self.logger.debug("No cut results in minimum altitude")

            return None

        new_polygons = polygon_split(polygon_union, LineString(min_candidate))
        return new_polygons
