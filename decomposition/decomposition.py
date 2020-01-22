"""Defining decomposition class."""
from copy import deepcopy
from typing import Dict, List, Tuple

from shapely.geometry import Polygon, Point

from utils import shapely_poly_to_canonical


class Decomposition():
    """Container class for storing decomposition and everything related to it."""
    __slots__ = (
        'polygon',
        'canonical_polygon',
        'num_cells',
        'canonical_cells',
        'cells',
        'canonical_robot_sites',
        'robot_sites',
    )

    def __init__(self, polygon: List[List]):
        """
        Args:
            polygon (List): Polygon in its canonical form.
        """
        self.canonical_polygon = deepcopy(polygon)
        self.polygon = Polygon(*polygon)

        self.num_cells = 0

        self.canonical_cells: Dict[int, List] = {}
        self.cells: Dict[int, Polygon] = {}

        self.canonical_robot_sites: Dict[int, Tuple] = {}
        self.robot_sites: Dict[int, Point] = {}

    def add_cell(self, cell: List[List]) -> int:
        """Adds a cell to the decomposition and returns its assigned index.

        Args:
            cell (List): List of veritcies.
        Returns:
            index assigned to this cell.
        """
        self.canonical_cells[self.num_cells] = deepcopy(cell)
        self.cells[self.num_cells] = Polygon(*cell)

        self.num_cells += 1

        return self.num_cells - 1

    def add_robot_site(self, robot_idx: int, site: Tuple[float, float]) -> bool:
        """Adds the robot site to the container.

        Args:
            robot_num (int): Index of the robot. Will be used to retrieve site.
            site (Tuple): A point representing starting location of robot.

        Returns:
            bool indicated success of add.
        """
        if robot_idx not in self.cells:
            return False

        self.robot_sites[robot_idx] = Point(site)
        self.canonical_robot_sites[robot_idx] = deepcopy(site)
        return True

    def __getitem__(self, key: int) -> Tuple[Polygon, Point]:
        """Override getitem."""
        # TODO: Implement checks.
        return self.cells[key], self.robot_sites[key]

    def __setitem__(self, key: int, val: Polygon):
        self.cells[key] = val
        self.canonical_cells[key] = shapely_poly_to_canonical(val)

    def items(self) -> List:
        return [(key, val, self.robot_sites[key]) for key, val in self.cells.items()]
