'''
TNS class : Soma
'''
import logging

import numpy as np
from scipy.spatial import ConvexHull  # pylint: disable=no-name-in-module
from scipy.spatial.qhull import QhullError  # pylint: disable=no-name-in-module

from tns.utils import TNSError
from tns.morphmath import rotation
from tns.generate import orientations


L = logging.getLogger()


class Soma:
    """TNS soma data structure. It contains the soma points and radius.

    Args:

        center (np.ndarray):
        radius (float): Radius of soma
        points (Iterable, optional): An iterable of 3D points

    """
    def __init__(self, center, radius, points=None):

        self.radius = float(radius)
        self._center = np.asarray(center, dtype=np.float64)
        self.points = [] if points is None else points

    @property
    def points(self):
        ''' Return the points list '''
        return self._points

    @points.setter
    def points(self, points):
        ''' Set the points list as a list of numpy arrays '''
        self._points = [np.asarray(p, dtype=np.float64) for p in points]

    @property
    def center(self):
        ''' Get center '''
        return self._center

    @center.setter
    def center(self, xyz):
        ''' Set center as a numpy array '''
        self._center = np.asarray(xyz, dtype=np.float64)

    def point_from_trunk_direction(self, phi, theta):
        '''Returns the direction of the unit vector and a point
        on the soma surface depending on the theta, phi angles.
        theta corresponds to the angle on the x-y plane.
        phi corresponds to the angle diversion on the z-axis.

        phis : polar angles
        thetas: azimuthal angles
        '''
        return np.array([
            self.center[0] + self.radius * np.cos(phi) * np.sin(theta),
            self.center[1] + self.radius * np.sin(phi) * np.sin(theta),
            self.center[2] + self.radius * np.cos(theta)], dtype=np.float64)

    def orientation_from_point(self, point):
        '''Returns the unit vector that corresponds to the orientation
        of a point on the soma surface.
        '''
        if np.allclose(point, self.center):
            raise ValueError('Point overlaps with soma center.')

        point = np.asarray([point])
        return orientations.points_to_orientations(self.center, point)[0]

    def contour_point(self, point):
        '''Keeps the c-y coordinates of the input point
        but replaces the third (z) coordinate with the equivalent
        soma-z in order to create a contour at the soma level.
        '''
        return np.array((point[0], point[1], self.center[2]), dtype=np.float64)


class SomaGrower:
    """Soma class"""

    def __init__(self, soma, context=None, rng=np.random):
        """TNS Soma Object

        Parameters:
            points: numpy array
        The (x, y, z, d)-coordinates of the x-y surface trace of the soma.
        """
        self.soma = soma
        self.context = context  # for future, hypothetical use
        self._rng = rng

    def add_points_from_trunk_angles(self, trunk_angles, z_angles):
        """Generates a sequence of points in the circumference of
        a circle of radius R, from a list of angles.
        trunk_angles correspond to the angles on the x-y plane,
        while z_angles correspond to the equivalent z-direction.

        trunk angles correspond to polar angles, phi
        z_angles correspond to azimuthal angles, theta
        """
        phis, thetas = orientations.trunk_to_spherical_angles(trunk_angles, z_angles)
        new_directions = orientations.spherical_angles_to_orientations(phis, thetas)
        return self.add_points_from_orientations(new_directions)

    def add_points_from_trunk_absolute_orientation(self, orientation, trunk_absolute_angles, z_angles):
        """Generates a sequence of points in the circumference of
        a circle of radius R, from a unit vector and a list of angles.
        """
        phis, thetas = orientations.trunk_absolute_orientation_to_spherical_angles(
            orientation, trunk_absolute_angles, z_angles)
        new_directions = orientations.spherical_angles_to_orientations(phis, thetas)
        return self.add_points_from_orientations(new_directions)

    def add_points_from_orientations(self, vectors):
        """Generates a sequence of points in the circumference of
        a circle of radius R, from a list of unit vectors.
        vectors is expected to be a list of orientations.
        """
        new_points = []

        for vect in vectors:

            phi, theta = rotation.spherical_from_vector(vect)
            point = self.soma.point_from_trunk_direction(phi, theta)
            new_points.append(point)

        self.soma.points.extend(new_points)
        return new_points

    def interpolate(self, points, interpolation=10):
        """Finds the convex hull from a list of points
        and returns a number of interpolation points that belong
        on this convex hull.
        interpolation: sets the minimum number of points to be generated.
        points: initial set of points
        """
        interpolation = np.max([3, interpolation])  # soma must have at least 3 points

        if len(points) >= interpolation:
            points_to_interpolate = points
        else:
            # Adds points from circle circumference to the soma points.
            angles = 2. * np.pi * self._rng.random(interpolation - len(points))
            x = self.soma.radius * np.sin(angles) + self.soma.center[0]
            y = self.soma.radius * np.cos(angles) + self.soma.center[1]
            z = np.full_like(angles, self.soma.center[2])
            points_to_interpolate = points + [[i, j, k] for i, j, k in zip(x, y, z)]

        # a convex hull from 2D points is guaranteed to be ordered
        xy_points = np.asarray(points_to_interpolate)[:, :2]

        try:
            selected = ConvexHull(xy_points).vertices
            return [points_to_interpolate[index] for index in selected]  # pylint: disable=not-an-iterable
        except QhullError as e:
            raise TNSError('Warning! Convex hull failed, contour soma generation failed.') from e

    def build(self, method='contour'):
        """Generates a soma from a list of points,
        in the circumference of a circle of radius R.
        The points will be saved into the neuron object and
        consist the first section of the cell.
        If interpolation is selected points will be generated
        until the expected number of soma points is reached.
        """
        if method == 'contour':
            return self._contour_soma()
        elif method == 'one_point':
            return self._one_point_soma()
        else:
            return self._original_soma()

    def _one_point_soma(self):
        """Generates a single point soma, representing a sphere
           including the center and the diameter.
        """
        soma_points = [self.soma.center]
        soma_diameters = [2.0 * self.soma.radius]
        return soma_points, soma_diameters

    def _contour_soma(self):
        """Generates a contour soma, that consists of all soma points.
           The contour must contain at least three points.
        """
        contour = [self.soma.contour_point(p) for p in self.soma.points]
        soma_pts = self.interpolate(contour)
        return soma_pts, np.zeros(len(soma_pts), dtype=np.float64)

    def _original_soma(self):
        """Returns the original soma points"""
        return self.soma.points, np.zeros(len(self.soma.points), dtype=np.float64)
