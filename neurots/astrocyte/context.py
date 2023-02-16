"""Space colonization context data structures."""

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
from scipy.special import logit

from neurots.astrocyte.point_cloud import PointCloud
from neurots.morphmath.point_array import DynamicPointArray
from neurots.utils import NeuroTSError

L = logging.getLogger(__name__)


class EndfeetTargets:
    """Store the Endfeet target points.

    Endfeet targets are the 3D points that influence the growth of the targeted tree growth.
    A tree will grow towards these points as long as they remain active.
    If a point is deactivated then it will no longer affect the grower it is assigned to.

    Args:
        coordinates (numpy.ndarray):
            Array of 3D points.

    Attributes:
        points (numpy.ndarray[numpy.single]):
            The coordinates of the 3D points that represent the endfeet
            targets.
        active (numpy.ndarray[bool]):
            A boolean mask, the same size as the number of points. A point
            is active when its corresponding boolean value in the active array
            is True.
    """

    def __init__(self, coordinates):
        self.points = np.asarray(coordinates, dtype=np.float32)
        self.active = np.ones(len(coordinates), dtype=bool)

    def __len__(self):
        """Return the number of active points."""
        return len(self.active)

    @property
    def active_points(self):
        """Returns the points that are still active."""
        return self.points[self.active]


class SpaceColonizationContext:
    """Context class for space colonization. It includes globally available information.

    Attributes:
        morphology_points (DynamicPointArray):
            The morphology points from the entire morphology, globally available by algorithms
            that need access to the morphology as a whole. For example repulsion needs to have
            access to all the neighboring points in the morphology to calculate the repulsion
            from them.
        endfeet_targets (EndfeetTargets):
            The targets for the targeting space colonization algorithm.
        field (Callable[float] -> float):
            The attraction field function that specifies how strong is the field as we approach
            the target. It takes a fraction which represents the ratio of distance of a point to
            the target over the distance from the soma to the target. That means that it will be
            zero when overlapping with the target and one if the point is overlapping with the
            soma position. It is used by the targeting space colonization algorithm to determine
            how much influenced the splitting direction should by the presence of the target.
        point_cloud (PointCloud):
            Seed point cloud for the space colonization queries.
        collision_handle (Callable[numpy.ndarray, float] -> bool):
            A callable function that takes a point and the segment length as input an returns
            if there is a collision or not. The segment length is used by probabilistic checks
            that scale the probability of colliding (soft collision with exponential decay from
            boundary distance), because it would affect the probability if a check is made
            every 1.0 um or every 0.1 um (10x more times).

    """

    def __init__(self, params):
        self.morphology_points = DynamicPointArray()

        if "endfeet_targets" in params:
            self.endfeet_targets = EndfeetTargets(params["endfeet_targets"])
        else:
            L.info("No endfeet targets available")
            self.endfeet_targets = None

        field = params["field"]
        if field["type"] == "logit":
            self.field = lambda x: field["slope"] * logit(x) + field["intercept"]
        else:
            raise NeuroTSError(f"{field['type']} function type is not available")

        sc_params = params["space_colonization"]
        self._params = sc_params

        if "point_cloud" in sc_params:
            self.point_cloud = PointCloud(sc_params["point_cloud"])
        else:
            raise NeuroTSError("point_cloud entry is not available in params")

        if "collision_handle" not in params or params["collision_handle"] is None:
            self.collision_handle = lambda *args: False
            L.info("No collision handle provided. There will be no collision checks.")
        else:
            self.collision_handle = params["collision_handle"]

    def kill_distance(self, segment_length):
        """Space colonization algorithm kill distance.

        Space colonization requires the removal of seed points (point cloud) around the newly
        created points. Kill distance is the threshold radius of the ball query to find the points
        to remove.

        Note:
            Instead of setting an absolute number it makes more sense for the
            kill distance to be factor multiplied by the segment length.

        For more details see:
        http://algorithmicbotany.org/papers/colonization.egwnp2007.large.pdf
        """
        kill_distance_factor = self._params["kill_distance_factor"]
        return kill_distance_factor * segment_length

    def influence_distance(self, segment_length):
        """Space colonization algorithm influence distance.

        Space colonization requires finding the seeds (point cloud) around points that will
        influence the growth direction. Influence distance is the threshold radius of the
        ball query to find the points to contribute.

        Note:
            Instead of setting an absolute number it makes more sense for the
            influence distance to be factor multiplied by the segment length.

        For more details see:
        http://algorithmicbotany.org/papers/colonization.egwnp2007.large.pdf
        """
        influence_distance_factor = self._params["influence_distance_factor"]
        return influence_distance_factor * segment_length
