from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import Point


def collinear_correction(decomp):

    for poly in decomp:
        boundary = poly[0]
        i = 0
        while i < len(boundary):
            p1 = boundary[i]
            p2 = boundary[(i+1)%len(boundary)]
            p3 = boundary[(i+2)%len(boundary)]
            if cuts.collinear(p1, p2, p3):
                del boundary[(i+1)%len(boundary)]
            i += 1

def compute_adjacency(decomposition):
    """
    Computes an adjacency relation for the polygons in the decomposition.
    In the effect, computes a graph where the nodes are polygons and the edges
    represent adjacency between polygons.

    Assumption:
        The polygons are considered adjacent if their boundaries intersect at an
        edge. If they only touch at a point, then will not be considered
        adjacent.

    Params:
        decomposition: A list of polygons in the canonical form.

    Returns:
        A 2_d list representing adjacency relation between polygons.
    """

    # Initialize the 2_d matric with None values.
    adj_matrix = [[False for i in range(len(decomposition))] for i in range(len(decomposition))]

    for poly_a_idx in range(len(decomposition)):
        for poly_b_idx in range(poly_a_idx + 1, len(decomposition)):

            poly_a = decomposition[poly_a_idx]
            poly_b = decomposition[poly_b_idx]
            if not poly_a.touches(poly_b):
                continue

            intersection = poly_a.intersection(poly_b)

            if isinstance(intersection, Point):
                continue

            adj_matrix[poly_a_idx][poly_b_idx] = True
            adj_matrix[poly_b_idx][poly_a_idx] = True

    return adj_matrix


if __name__ == '__main__':

    print("\n_sanity tests for pairwise reoptimization.\n")

    poly_set = [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], []),
                Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], []),
                Polygon([(1, 1), (2, 1), (2, 2), (1, 2)], []),
                Polygon([(0, 1), (1, 1), (1, 2), (0, 2)], [])]
    print(compute_adjacency(poly_set))

    poly_set = [Polygon([(0, 0), (1, 0), (1, 1), (0.5, 0.5), (0, 1)], []),
                Polygon([(1, 0), (2, 0), (2, 1), (1, 1)], []),
                Polygon([(1, 1), (2, 1), (2, 2), (1, 2)], []),
                Polygon([(0, 1), (0.5, 0.5), (1, 1), (1, 2), (0, 2)], [])]
    print(compute_adjacency(poly_set))
