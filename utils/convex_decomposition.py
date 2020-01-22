"""Module containing 3rd party convex decomposition of polygons."""
from shapely.geometry import Polygon as ShapelyPolygon
from py2d.Math import Polygon

from decomposition import Decomposition
from utils import shapely_poly_to_canonical


def greedy_decomposition(polygon: ShapelyPolygon) -> Decomposition:
    """Wrapper for 3rd party convex decomposition of polygons with holes.

    Args:
        polygon (ShapelyPolygon): Shapely object representing the polygon to be decomposed.

    Returns:
        Decomposition representing convex greedy decomposition of the polygon.
    """

    exterior, holes = shapely_poly_to_canonical(polygon)

    new_poly = Polygon.from_tuples(exterior)
    new_holes = [Polygon.from_tuples(hole) for hole in holes]

    convex_decomposition = Polygon.convex_decompose(new_poly, new_holes)
    assert convex_decomposition, "Greedy convex decomposition FAILED."

    decomposition = Decomposition([exterior, holes])
    for poly in convex_decomposition:
        # Since it's convex decomposition, there will be no holes.
        decomposition.add_cell([poly.as_tuple_list(), []])

    return decomposition
