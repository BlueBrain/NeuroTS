"""NeuroTS class: Soma."""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

import numpy as np
from scipy.spatial import ConvexHull

try:
    # The QhulError was moved in scipy >= 1.8 so if the import fails the old location is imported
    from scipy.spatial import QhullError
except ImportError:  # pragma: no cover
    from scipy.spatial.qhull import QhullError

from neurots.generate import orientations
from neurots.morphmath import rotation
from neurots.utils import NeuroTSError

L = logging.getLogger()


class Soma:
    """NeuroTS soma data structure.

    It contains the soma points and radius.

    Args:
        center (numpy.ndarray): The center of the soma.
        radius (float): The radius of the soma.
        points (list[list[float]], optional): An iterable of 3D points.
    """

    def __init__(self, center, radius, points=None):
        self.radius = float(radius)
        self._center = np.asarray(center, dtype=np.float64)
        self.points = [] if points is None else points

    @property
    def points(self):
        """Return the points list."""
        return self._points

    @points.setter
    def points(self, points):
        """Set the points list as a list of numpy arrays."""
        self._points = [np.asarray(p, dtype=np.float64) for p in points]

    @property
    def center(self):
        """Get the center."""
        return self._center

    @center.setter
    def center(self, xyz):
        """Set center as a numpy array."""
        self._center = np.asarray(xyz, dtype=np.float64)

    def point_from_trunk_direction(self, phi, theta):
        """Return the coordinates of a point on the soma surface from the given theta, phi angles.

        Args:
            phi (list[float]): The polar angle (i.e. on the z-axis).
            theta (list[float]): The azimuthal angle (i.e. on the x-y plane).
        """
        return np.array(
            [
                self.center[0] + self.radius * np.cos(phi) * np.sin(theta),
                self.center[1] + self.radius * np.sin(phi) * np.sin(theta),
                self.center[2] + self.radius * np.cos(theta),
            ],
            dtype=np.float64,
        )

    def orientation_from_point(self, point):
        """Return the orientation from the soma center to a point on the soma surface."""
        if np.allclose(point, self.center):
            raise ValueError("Point overlaps with soma center.")

        point = np.asarray([point])
        return orientations.points_to_orientations(self.center, point)[0]

    def contour_point(self, point):
        """Create a contour point from a given point.

        Keeps the x-y coordinates of the input point but replaces the third (z) coordinate with the
        equivalent soma-z in order to create a contour at the soma level.
        """
        return np.array((point[0], point[1], self.center[2]), dtype=np.float64)


class SomaGrower:
    """Soma class.

    Args:
        soma (Soma): The soma that will grow.
        context (Any): The context used for the section.
        rng (numpy.random.Generator): The random number generator to use.
    """

    def __init__(self, soma, context=None, rng=np.random):
        """Constructor of the Soma class."""
        self.soma = soma
        self.context = context  # for future, hypothetical use
        self._rng = rng

    def add_points_from_trunk_angles(self, trunk_angles, z_angles, phi_interval=None):
        """Generate points on the soma surface from a list of angles.

        Args:
            trunk_angles (list[float]): The polar angles (phi in spherical coordinates).
            z_angles (list[float]): The azimuthal angles (theta in spherical coordinates).
            phi_interval (tuple[float, float]): The interval in which the trunks should be added.

        Returns:
            list[list[float]]: The new points.
        """
        phis, thetas = orientations.trunk_to_spherical_angles(trunk_angles, z_angles, phi_interval)
        new_directions = orientations.spherical_angles_to_orientations(phis, thetas)
        return self.add_points_from_orientations(new_directions)

    def add_points_from_trunk_absolute_orientation(
        self, orientation, trunk_absolute_angles, z_angles
    ):
        """Generate points on the soma surface from a direction and a list of angles.

        Args:
            orientation (list[float]): The trunk orientation.
            trunk_absolute_angles (list[float]): The polar angles (phi in spherical coordinates).
            z_angles (list[float]): The azimuthal angles (theta in spherical coordinates).

        Returns:
            list[list[float]]: The new points.
        """
        phis, thetas = orientations.trunk_absolute_orientation_to_spherical_angles(
            orientation, trunk_absolute_angles, z_angles
        )
        new_directions = orientations.spherical_angles_to_orientations(phis, thetas)
        return self.add_points_from_orientations(new_directions)

    def add_points_from_orientations(self, vectors):
        """Generate points on the soma surface from a list of unit vectors.

        Args:
            vectors (list[list[float]]): The list of orientations.

        Returns:
            list[list[float]]: The new points.
        """
        new_points = []

        for vect in vectors:
            phi, theta = rotation.spherical_from_vector(vect)
            point = self.soma.point_from_trunk_direction(phi, theta)
            new_points.append(point)

        self.soma.points.extend(new_points)
        return new_points

    def interpolate(self, points, interpolation=10):
        """Return the interpolation points on the convex hull.

        Finds the convex hull from a list of points and returns a number of interpolation points
        that belong on this convex hull.

        Args:
            points (list[float]): Initial set of points.
            interpolation (int): The the minimum number of points to be generated.

        Returns:
            list[list[float]]: The list of interpolated points.
        """
        interpolation = np.max([3, interpolation])  # soma must have at least 3 points

        if len(points) >= interpolation:
            points_to_interpolate = points
        else:
            # Adds points from circle circumference to the soma points.
            angles = 2.0 * np.pi * self._rng.random(interpolation - len(points))
            x = self.soma.radius * np.sin(angles) + self.soma.center[0]
            y = self.soma.radius * np.cos(angles) + self.soma.center[1]
            z = np.full_like(angles, self.soma.center[2])
            points_to_interpolate = points + [[i, j, k] for i, j, k in zip(x, y, z)]

        # a convex hull from 2D points is guaranteed to be ordered
        xy_points = np.asarray(points_to_interpolate)[:, :2]

        try:
            selected = ConvexHull(xy_points).vertices
            return [
                points_to_interpolate[index]
                for index in selected  # pylint: disable=not-an-iterable
            ]
        except QhullError as e:
            raise NeuroTSError(
                "Warning! Convex hull failed, contour soma generation failed."
            ) from e

    def build(self, method="contour"):
        """Generates a soma, depending on the method used.

        The points will be saved into the neuron object and consist the first section of the cell.
        If interpolation is selected points will be generated until the expected number of soma
        points is reached.

        Args:
            method (str): The method used to build the soma.

        Returns:
            tuple[list[float], list[float]]: The points and diameters of the built soma.
        """
        if method == "contour":
            return self._contour_soma()
        elif method == "one_point":
            return self._one_point_soma()
        else:
            return self._original_soma()

    def _one_point_soma(self):
        """Generate a single point soma.

        This kind of soma is represented by a sphere including the center and the diameter.

        Returns:
            tuple[list[float], list[float]]: The points and diameters of the built soma.
        """
        soma_points = [self.soma.center]
        soma_diameters = [2.0 * self.soma.radius]
        return soma_points, soma_diameters

    def _contour_soma(self):
        """Generate a contour soma, that consists of all soma points.

        The contour must contain at least three points.

        Returns:
            tuple[list[float], list[float]]: The points and diameters of the built soma.
        """
        contour = [self.soma.contour_point(p) for p in self.soma.points]
        soma_pts = self.interpolate(contour)
        return soma_pts, np.zeros(len(soma_pts), dtype=np.float64)

    def _original_soma(self):
        """Returns the original soma points.

        Returns:
            tuple[list[float], list[float]]: The points and diameters of the built soma.
        """
        return self.soma.points, np.zeros(len(self.soma.points), dtype=np.float64)
