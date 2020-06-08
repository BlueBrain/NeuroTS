'''
TNS class : Soma
'''
import logging

import numpy as np
from scipy.spatial import ConvexHull  # pylint: disable=no-name-in-module
from scipy.spatial.qhull import QhullError  # pylint: disable=no-name-in-module

from tns.utils import TNSError
from tns.morphmath import rotation
from tns.morphmath.utils import norm

L = logging.getLogger()


class SomaGrower(object):
    """Soma class"""

    def __init__(self, initial_point, radius=1.0, context=None):
        """TNS Soma Object

        Parameters:
            points: numpy array
        The (x, y, z, d)-coordinates of the x-y surface trace of the soma.
        """
        self._points = []
        self.radius = float(radius)
        self._center = np.asarray(initial_point, dtype=np.float)
        self.context = context  # for future, hypothetical use

    @property
    def points(self):
        ''' Return the points list '''
        return self._points

    @points.setter
    def points(self, points):
        ''' Set the points list as a list of numpy arrays '''
        self._points = [np.asarray(p, dtype=np.float) for p in points]

    @property
    def center(self):
        ''' Get center '''
        return self._center

    @center.setter
    def center(self, xyz):
        ''' Set center as a numpy array '''
        self._center = np.asarray(xyz, dtype=np.float)

    def point_from_trunk_direction(self, phi, theta):
        '''Returns the direction of the unit vector and a point
        on the soma surface depending on the theta, phi angles.
        theta corresponds to the angle on the x-y plane.
        phi corresponds to the angle diversion on the z-axis.

        phi : polar angle
        theta: azimuthal angle
        '''
        return np.array((self.center[0] + self.radius * np.cos(phi) * np.sin(theta),
                         self.center[1] + self.radius * np.sin(phi) * np.sin(theta),
                         self.center[2] + self.radius * np.cos(theta)), dtype=np.float)

    def orientation_from_point(self, point):
        '''Returns the unit vector that corresponds to the orientation
        of a point on the soma surface.
        '''
        # pylint: disable=assignment-from-no-return
        vector = np.subtract(point, self.center)

        if np.allclose(vector, 0.0):
            raise ValueError('Orientation point overlaps with soma center.')

        return vector / norm(vector)

    def contour_point(self, point):
        '''Keeps the c-y coordinates of the input point
        but replaces the third (z) coordinate with the equivalent
        soma-z in order to create a contour at the soma level.
        '''
        return np.array((point[0], point[1], self.center[2]), dtype=np.float)

    def add_points_from_trunk_angles(self, trunk_angles, z_angles):
        """Generates a sequence of points in the circumference of
        a circle of radius R, from a list of angles.
        trunk_angles correspond to the angles on the x-y plane,
        while z_angles correspond to the equivalent z-direction.

        trunk angles correspond to polar angles, phi
        z_angles correspond to azimuthal angles, theta
        """
        sortIDs = np.argsort(trunk_angles)
        equiangle = 2. * np.pi / len(trunk_angles)

        sorted_phi_devs = np.asarray(trunk_angles)[sortIDs]
        sorted_thetas = np.asarray(z_angles)[sortIDs]

        new_points = []

        for i, (theta, dphi) in enumerate(zip(sorted_thetas, sorted_phi_devs)):

            phi = (i + 1) * equiangle + dphi
            point = self.point_from_trunk_direction(phi, theta)
            new_points.append(point)

        self.points.extend(new_points)

        return new_points

    def add_points_from_orientations(self, vectors):
        """Generates a sequence of points in the circumference of
        a circle of radius R, from a list of unit vectors.
        vectors is expected to be a list of orientations.
        """
        new_points = []

        for vect in vectors:

            phi, theta = rotation.spherical_from_vector(vect)
            point = self.point_from_trunk_direction(phi, theta)
            new_points.append(point)

        self.points.extend(new_points)

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
            angles = 2. * np.pi * np.random.rand(interpolation - len(points))
            x = self.radius * np.sin(angles) + self.center[0]
            y = self.radius * np.cos(angles) + self.center[1]
            z = np.full_like(angles, self.center[2])
            points_to_interpolate = points + [[i, j, k] for i, j, k in zip(x, y, z)]

        # a convex hull from 2D points is guaranteed to be ordered
        xy_points = np.asarray(points_to_interpolate)[:, :2]

        try:
            selected = ConvexHull(xy_points).vertices
            return [points_to_interpolate[index] for index in selected]  # pylint: disable=not-an-iterable
        except QhullError:
            raise TNSError('Warning! Convex hull failed, contour soma generation failed.')

    def build(self, method='contour'):
        """Generates a soma from a list of points,
        in the circumference of a circle of radius R.
        The points will be saved into the neuron object and
        consist the first section of the cell.
        If interpolation is selected points will be generated
        until the expected number of soma points is reached.
        """
        if method == 'contour':
            return self.contour_soma()
        elif method == 'one_point':
            return self.one_point_soma()
        else:
            return self.original_soma()

    def one_point_soma(self):
        """Generates a single point soma, representing a sphere
           including the center and the diameter.
        """
        soma_points = [self.center]
        soma_diameters = [2.0 * self.radius]
        return soma_points, soma_diameters

    def contour_soma(self):
        """Generates a contour soma, that consists of all soma points.
           The contour must contain at least three points.
        """
        contour = [self.contour_point(p) for p in self.points]
        soma_pts = self.interpolate(contour)
        return soma_pts, np.zeros(len(soma_pts), dtype=np.float)

    def original_soma(self):
        """Returns the original somata points"""
        return self.points, np.zeros(len(self.points), dtype=np.float)
