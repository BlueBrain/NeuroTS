'''
TNS class : Soma
'''
import logging

import numpy as np

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
        self.points3D = []
        self.context = context  # for future, hypothetical use
        self.radius = radius
        self.center = initial_point

    def point_from_trunk_direction(self, phi, theta):
        '''Returns the direction of the unit vector and a point
        on the soma surface depending on the theta, phi angles.
        theta corresponds to the angle on the x-y plane.
        phi corresponds to the angle diversion on the z-axis.
        '''
        point_on_soma = [self.center[0] + self.radius * np.cos(phi) * np.sin(theta),
                         self.center[1] + self.radius * np.sin(phi) * np.sin(theta),
                         self.center[2] + self.radius * np.cos(theta)]

        return point_on_soma

    def orientation_from_point(self, point):
        '''Returns the unit vector that corresponds to the orientation
        of a point on the soma surface.
        '''
        # pylint: disable=assignment-from-no-return
        point_on_soma = np.subtract(np.array(point), np.array(self.center))

        return point_on_soma / norm(point_on_soma)

    def contour_point(self, point):
        '''Keeps the c-y coordinates of the input point
        but replaces the third (z) coordinate with the equivalent
        soma-z in order to create a contour at the soma level.
        '''
        return [point[0], point[1], self.center[2]]

    def add_points_from_trunk_angles(self, trunk_angles, z_angles):
        """Generates a sequence of points in the circumference of
        a circle of radius R, from a list of angles.
        trunk_angles correspond to the angles on the x-y plane,
        while z_angles correspond to the equivalent z-direction.
        """
        sortIDs = np.argsort(trunk_angles)
        angle_norm = 2. * np.pi / len(trunk_angles)
        new_points3D = []

        for i, theta in enumerate(np.array(trunk_angles)[sortIDs]):

            phi = np.array(z_angles)[sortIDs][i]
            ang = (i + 1) * angle_norm
            point = self.point_from_trunk_direction(theta + ang, phi)

            new_points3D.append(point)

        self.points3D.extend(new_points3D)

        return new_points3D

    def add_points_from_orientations(self, vectors):
        """Generates a sequence of points in the circumference of
        a circle of radius R, from a list of unit vectors.
        vectors is expected to be a list of orientations.
        """
        from tns.morphmath import rotation
        new_points3D = []

        for vect in vectors:

            phi, theta = rotation.spherical_from_vector(vect)
            point = self.point_from_trunk_direction(phi, theta)
            new_points3D.append(point)

        self.points3D.extend(new_points3D)

        return new_points3D

    @staticmethod
    def interpolate(points3D, interpolation=3):
        """Finds the convex hull from a list of points
        and returns a number of interpolation points that belong
        on this convex hull.
        interpolation: sets the minimum number of points to be generated.
        points: initial set of points
        """
        from scipy.spatial import ConvexHull  # pylint: disable=no-name-in-module

        fail_msg = 'Warning! Convex hull failed. Original points were saved instead'

        if len(points3D) > interpolation:
            hull = ConvexHull(points3D)
            selected = np.array(points3D)[hull.vertices]
            if len(selected) > interpolation:
                return selected.tolist()
            elif len(points3D) > interpolation:
                L.warning(fail_msg)
                return points3D.tolist()
            L.warning(fail_msg)
            return interpolation * points3D.tolist()
        L.warning(fail_msg)
        return interpolation * points3D.tolist()

    def generate_neuron_soma_points3D(self, interpolation=3):
        """Generates a soma from a list of points3D,
        in the circumference of a circle of radius R.
        The points will be saved into the neuron object and
        consist the first section of the cell.
        If interpolation is selected points will be generated
        until the expected number of soma points is reached.
        """
        # Soma 3D points as a contour to be saved in neuron.
        contour = np.array([self.contour_point(p) for p in self.points3D])

        if interpolation is None:
            return contour
        return self.interpolate(contour, interpolation=interpolation)
