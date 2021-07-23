'''Util functions useful for general purposes'''

from math import sqrt
import numpy as np
# TODO: use KDTree when python3.6 is dropped and scipy>=1.6 is available
from scipy.spatial import cKDTree as KDTree


# The smallest representable positive number such that 1.0 + eps != 1.0
# around 1e-7 for float32
EPS = np.finfo(np.float32).eps


def get_random_point(D=1.0, random_generator=np.random):
    '''
    Get 3-d coordinates of a new random point.
    The distance between the produced point and (0,0,0)
    is given by the value D.
    '''
    # pylint: disable=assignment-from-no-return
    phi = random_generator.uniform(0., 2. * np.pi)
    theta = np.arccos(random_generator.uniform(-1.0, 1.0))

    sn_theta = np.sin(theta)

    x = D * np.cos(phi) * sn_theta
    y = D * np.sin(phi) * sn_theta
    z = D * np.cos(theta)

    return np.array((x, y, z))


def norm(vector):
    """Returns the norm of the numpy array"""
    return sqrt(vector.dot(vector))


def normalize_inplace(vector):
    """Normalizes a vector in place and returns it. It is faster
    because it avoids a copy but be careful when using it because
    it mutates its argument.
    """
    vector /= norm(vector)
    return vector


def normalize_vectors(vectors):
    """Returns normalized vectors"""
    return vectors / np.linalg.norm(vectors, axis=1)[:, np.newaxis]


def from_to_direction(point1, point2, return_length=False):
    '''Returns weight and normalized direction to target '''
    vector = point2 - point1
    length = norm(vector)

    if return_length:
        return vector / length, length

    return vector / length


def in_same_halfspace(vectors, normal, return_dots=False):
    """Returns a mask of vectors that are in the same halfspace
    as its normal
    """
    dots = vectors.dot(normal)
    mask = dots > EPS
    if return_dots:
        return mask, dots[mask]
    return mask


def in_squared_proximity(point1, point2, squared_proximity):
    """Returns true if point1 is in the proximity of point2"""
    vector = point2 - point1
    return vector.dot(vector) < squared_proximity + EPS


def ball_query(points, ball_center, ball_radius):
    """Returns the ids of the tree_points that are located inside the ball
    with center point and radius
    """
    tree = KDTree(
        points,
        compact_nodes=False,
        copy_data=False,
        leafsize=2**10,
        balanced_tree=False
    )

    return np.fromiter(tree.query_ball_point(ball_center, ball_radius), dtype=np.int)


def upper_half_ball_query(points, ball_center, ball_radius, direction):
    """Returns the points that are included in the hemisphere that has
    ref_point as center, hemisphere_radius and are in the same halfspace
    as direction.
    """
    ids = ball_query(points, ball_center, ball_radius)

    if ids.size == 0:
        return ids

    return ids[in_same_halfspace(points[ids] - ball_center, direction)]
