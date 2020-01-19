"""High level optimizer that runs iterations."""
from typing import Dict, List, Tuple

from shapely.geometry import LineString, Polygon, Point

from decomposition_processing import compute_adjacency
from chi import compute_chi
from reopt_recursion import dft_recursion
from log_utils import get_logger


class ChiOptimizer():
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

            if not dft_recursion(decomposition,
                                 adjacency_matrix,
                                 sorted_chi_costs[0][0],
                                 cell_to_site_map,
                                 self.radius,
                                 self.lin_penalty,
                                 self.ang_penalty):
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


if __name__ == '__main__':

    # If package is launched from cmd line, run sanity checks
    print("\n_sanity tests for the reoptimizer.\n")

    q = {0: (0.0,0.0), 1: (10.0,0.0), 2: (10.0,1.0), 3: (0.0,1.0)}
    decomposition_ = [[[(0.0,0.0),(10.0,0.0), (10.0,0.5)],[]], [[(0.0,0.0),(10.0,0.5),(10.0,1.0),(5.0,0.5)],[]], [[(5.0,0.5),(10.0,1.0),(0.0,1.0)],[]], [[(0.0,0.0),(5.0,0.5),(0.0,1.0)],[]]]

    optimizer = ChiOptimizer()

    optimizer.run_iterations(decomposition=decomposition_,
                             cell_to_site_map=q,
                             original_chi_costs=[],
                             new_chi_costs=[])
