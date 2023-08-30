"""Basic class for TreeGrower Algorithms for space colonization."""

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
from numpy.core.umath import clip

from neurots.astrocyte.tmd_utils import barcodes_greater_than_distance
from neurots.astrocyte.tmd_utils import scale_barcode
from neurots.generate.algorithms.common import section_data
from neurots.generate.algorithms.tmdgrower import TMDAlgo
from neurots.morphmath import sample
from neurots.morphmath.bifurcation import directional
from neurots.morphmath.utils import from_to_direction
from neurots.morphmath.utils import in_squared_proximity
from neurots.morphmath.utils import norm as vectorial_norm
from neurots.morphmath.utils import upper_half_ball_query

L = logging.getLogger(__name__)


ENDFOOT_SQUARED_DISTANCE = 5.0


def _majorize_process(process, stop, target_distance):
    """Curates the non-major processes to apply a gradient to large components.

    .. note::
        If the expected maximum length is larger that target distance, then a process type of major
        will be returned. Otherwise, the initial type process will be returned.

    Args:
        process (str): Process type.
        stop (StopCriteria): Section stop criteria.
        target_distance (float): Target distance to check the stop criteria against.

    Returns:
        str: process type
    """
    difference = stop.expected_maximum_length()
    if not np.isinf(difference) and difference > target_distance:
        return "major"
    return process


def _repulsion(points, current_point, length_constant):
    """Calculate the repulsion from the points to the ref_point.

    The length_constant determines the decay rate of the exponential contribution.

    Only the points that are inside the hemisphere with radius cutoff_distance and in the
    same halfspace as section_radius are taken into account.

    Args:
        points (numpy.ndarray): Seed points, the sources of the repulsion force.
        current_point (numpy.ndarray): Reference point on which the repulsion will be applied.
        length_constant (float): Exponential's decay length constant for repulsion strength.

    Returns:
        numpy.ndarray: The average absolute repulsion contribution.
    """
    if len(points) == 0:
        return np.zeros(3, dtype=np.float32)

    vectors = points - current_point

    decay_rate = 1.0 / length_constant
    lengths = np.linalg.norm(vectors, axis=1)
    u_vectors = vectors / lengths[:, None]

    contributions = np.exp(lengths * -decay_rate)
    return contributions.dot(u_vectors) / len(vectors)


def _fallback_strategy(section_direction, angles, repulsion):
    """Directional splitting.

    dir1 is always same as section_direction plus the repulsion.
    dir2 is determined by the angles and the repulsion.

    Args:
        section_direction (numpy.ndarray): The direction of the section.
        angles (list): The list angle distribution to sample from.
        repulsion (numpy.ndarray): The absolute repulsion contribution.

    Returns:
        tuple[numpy.ndarray, numpy.ndarray]: first and second split directions.
    """
    dir1 = section_direction - repulsion
    dir1 /= vectorial_norm(dir1)

    _, dir2 = directional(dir1, angles=angles)

    dir2 -= repulsion
    dir2 /= vectorial_norm(dir2)

    return dir1, dir2


def _colonization_strategy_primary(previous_direction, vectors_to_seeds, repulsion):
    """Compute directions with primary strategy.

    .. note::
        dir1 is calculated by the mean direction from the vectors_to_seeds.

        dir2 is determined by the direction that maximized its angle to dir1.

        Both dir1 and dir2 and dir2 are affected by repulsion.

    Args:
        previous_direction (numpy.ndarray): The previous section direction.
        vectors_to_seeds (numpy.ndarray): Vectors from current point to seeds.
        repulsion (numpy.ndarray): Absolute repulsion contribution.

    Returns:
        tuple[numpy.ndarray, numpy.ndarray]: first and second split directions.
    """
    vectors_to_seeds = vectors_to_seeds - repulsion
    lengths = np.linalg.norm(vectors_to_seeds, axis=1)
    uvecs = vectors_to_seeds / lengths[:, None]

    dir1 = previous_direction - repulsion
    dir1 /= vectorial_norm(dir1)

    # most negative dot product of unit vecs corresponds to the largest angle
    pos2 = np.argmin(uvecs.dot(dir1))
    dir2 = uvecs[pos2]

    return dir1, dir2


def _colonization_strategy_secondary(vectors_to_seeds, repulsion):
    """Compute directions with secondary strategy.

    .. note::
        dir1 is calculated by the mean direction from the vectors_to_seeds.

        dir2 is determined by the direction that maximized its angle to dir1.

        Both dir1 and dir2 and dir2 are affected by repulsion.

    Args:
        vectors_to_seeds (numpy.ndarray): Vectors from current point to seeds.
        repulsion (numpy.ndarray): Absolute repulsion contribution.

    Returns:
        tuple[numpy.ndarray, numpy.ndarray]: The first and second split directions.
    """
    vectors_to_seeds = vectors_to_seeds - repulsion
    lengths = np.linalg.norm(vectors_to_seeds, axis=1)
    uvecs = vectors_to_seeds / lengths[:, None]

    pos1 = np.argmin(lengths)
    dir1 = uvecs[pos1]

    # most negative dot product of unit vecs corresponds to the largest angle
    pos2 = np.argmin(uvecs.dot(dir1))
    dir2 = uvecs[pos2]

    return dir1, dir2


def _colonization_split(section, angles, parameters, context):
    """Creates a bifurcation using the space colonization algorithm.

    Args:
        section (SectionGrower): The current section
        angles (list): Angle distribution for sampling
        parameters (dict): Algorithm's parameters
        context (SpaceColonizationContext): External space colonization data

    Returns:
        tuple[numpy.ndarray, str, numpy.ndarray, str]:
            A tuple containing the following values:

            * first direction
            * first section type
            * second direction
            * second section type

    .. note::
        A repulsion contribution is calculated first from the morphology points
        that are around the bifurcation point. If there are no points available
        the repulsion will be zero.

        If the section grower is a major type:

        A partial ball query is performed to find all the point cloud seeds
        that are around the bifurcation point. The primary colonization strategy
        is then used where the first direction is the same as the direction of the
        section plus the repulsion and the second one is chosen so that it maximized
        the angle with the first direction.

        if the section grower is not a major type:

        A half bal query is perfmored along the direction of the section to find the
        point cloud seeds around the bifurcation point. The secondary colonization
        strategy is then used where the first direction is chosen by the closest seed
        to the bifurcation point and the second one from the direction that maximizes
        the direction to the first one.

        In both cases if not enough seeds are found the strategy will fall back to a
        directional splitting sampling from the bio angles. It will also fallback if
        the two new directions are identical. It's a rare case but it can happen given
        overlapping point cloud seeds.
    """
    current_point = section.last_point
    section_direction = section.direction

    segment_length = parameters["step_size"]["norm"]["mean"]
    kill_distance = context.kill_distance(segment_length)
    influence_distance = context.influence_distance(segment_length)

    point_cloud = context.point_cloud

    # current points of the morphology contributing to self repulsion
    # last point is current_point, therefore we should ignore it
    morphology_points = context.morphology_points.data[:-1]

    # repulsion contribution only from points in the hemisphere aligned to direction
    ids = upper_half_ball_query(morphology_points, current_point, kill_distance, section_direction)
    repulsion = _repulsion(morphology_points[ids], current_point, kill_distance)

    if section.process == "major":
        seed_ids = point_cloud.partial_ball_query(
            current_point,
            influence_distance,
            section_direction,
            np.pi / 3.0,
            np.pi / 2.5,
        )

        if len(seed_ids) < 2:
            dir1, dir2 = _fallback_strategy(section_direction, angles, repulsion)
        else:
            vectors_to_seeds = point_cloud.points[seed_ids] - current_point
            dir1, dir2 = _colonization_strategy_primary(
                section_direction, vectors_to_seeds, repulsion
            )
    else:
        seed_ids = point_cloud.upper_half_ball_query(
            current_point, influence_distance, section_direction
        )

        if len(seed_ids) < 2:
            dir1, dir2 = _fallback_strategy(section_direction, angles, repulsion)
        else:
            vectors_to_seeds = point_cloud.points[seed_ids] - current_point
            dir1, dir2 = _colonization_strategy_secondary(vectors_to_seeds, repulsion)

    if np.allclose(dir1, dir2):
        L.warning(
            "Splitting directions are identical. Use of fallback strategy to recalculate them."
        )
        dir1, dir2 = _fallback_strategy(section_direction, angles, repulsion)

    return dir1, section.process, dir2, "secondary"


def _add_attraction_bias(
    current_point, target_point, max_target_distance, direction, attraction_function
):
    """Adds a bias to the direction whose magnitude depends on the attraction function.

    The attraction function takes as an input the ratio of the distance of the current
    point to the target over the total distance of the target from the soma.

    Args:
        current_point (numpy.ndarray): The reference point.
        target_point (numpy.ndarray): The attractor point.
        max_target_distance (float): The distance from soma center to attraction point.
        direction (numpy.ndarray): Section direction.
        attraction_function (Callable[float] -> float): Attraction strength function handle.

    Returns:
        numpy.ndarray: The new direction.
    """
    target_direction, magnitude = from_to_direction(current_point, target_point, return_length=True)

    fraction = clip(magnitude / max_target_distance, 0.0, 1.0)
    a = clip(attraction_function(fraction), 0.0, 1.0)

    new_direction = a * target_direction + (1.0 - a) * direction
    new_direction /= vectorial_norm(new_direction)

    return new_direction


def _colonization_split_with_target_influence(section, angles, parameters, context):
    """Creates a bifurcation using the space colonization algorithm.

    Args:
        section (SectionGrower): The current section.
        angles (list): Angle distribution for sampling.
        parameters (dict): Algorithm's parameters.
        context (SpaceColonizationContext): External space colonization data.

    Returns:
        tuple[numpy.ndarray, str, numpy.ndarray, str]:
            A tuple containing the following values:

            * first direction
            * first section type
            * second direction
            * second section type

    .. note::
        Bifurcation directions are calculated based on the space colonization split. If
        the endfoot target is active and is close to the bifurcation point, then the the
        second section type will become an endfoot and the target will be exclusive to it,
        rendering it not active. The second direction will be overridden with the direction
        to the target.

        If the target is not in proximity and the section has a major type, an attraction bias
        is added towards the target that depends on the strength of the attraction field. If it
        isn't a major type, it can become major via the majorization function. In order to be
        majorized the bar must be a long one, i.e. longer than 80% of the distance from the tree
        start to the soma.
    """
    process1, process2 = section.process, "secondary"

    current_point = section.last_point
    target_id = section.stop_criteria["target_id"]

    dir1, _, dir2, _ = _colonization_split(section, angles, parameters, context)

    if not context.endfeet_targets.active[target_id]:
        return dir1, process1, dir2, process2

    target_point = context.endfeet_targets.points[target_id]

    if in_squared_proximity(current_point, target_point, ENDFOOT_SQUARED_DISTANCE):
        # this section will become the endfoot section that will connect to the target
        process2 = "endfoot"

        # make the target invisible for the rest of the section growers
        context.endfeet_targets.active[target_id] = False
        dir2 = from_to_direction(current_point, target_point)
    else:
        max_target_distance = parameters["distance_soma_target"]
        if process1 == "major":
            dir1 = _add_attraction_bias(
                current_point,
                target_point,
                max_target_distance,
                dir1,
                section.context.field,
            )
        else:
            process1 = _majorize_process(
                process1,
                section.stop_criteria["TMD"],
                parameters["bias"] * max_target_distance,
            )

    return dir1, process1, dir2, process2


class SpaceColonization(TMDAlgo):
    """Algorithm for growing a tree using a variation of the space colonization algorithm.

    A spatial colonization context is required, which will provide access
    to the seed point cloud for the respective queries needed for the splitting strategies.

    The neurots space colonization algorithm operates using the following data:

    - SpaceColonizationContext
        - Seeds point cloud
        - Space colonization parameters (kill and influence distance)
    """

    def select_persistence(self, input_data, random_generator=np.random):
        """Select the persistence.

        The persistaece is randomly selected from the barcodes the max radial of which
        is greater or equal to the distance from the soma to the domain face.

        Args:
            input_data (dict): The input data parameters.
            random_generator (numpy.random.Generator): The random number generator to use.

        Returns:
            Barcode: The topology barcode.
        """
        if "distance_to_domain" not in self.params:
            return super().select_persistence(input_data, random_generator)

        target_distance = self.params["distance_to_domain"]

        persistence = sample.ph(
            barcodes_greater_than_distance(input_data["persistence_diagram"], target_distance),
            random_generator,
        )

        if self.params["barcode_scaling"]:
            persistence = scale_barcode(persistence, target_distance)

        return persistence

    def bifurcate(self, current_section):
        """When the section bifurcates two new sections need to be created.

        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        self.barcode.remove_bif(current_section.stop_criteria["TMD"].bif_id)
        ang = self.barcode.angles[current_section.stop_criteria["TMD"].bif_id]

        dir1, type1, dir2, type2 = _colonization_split(
            current_section, ang, self.params, self.context
        )

        first_point = np.array(current_section.last_point)

        stop1, stop2 = self.get_stop_criteria(current_section)

        return (
            section_data(dir1, first_point, stop1, type1),
            section_data(dir2, first_point, stop2, type2),
        )


class SpaceColonizationTarget(SpaceColonization):
    """A target is specified for this algorithm.

    The tree grows biased from the target and when it reaches it, it stops being influenced by the
    point.
    """

    def select_persistence(self, input_data, random_generator=np.random):
        """Select the persistence.

        The persistaece is randomly selected from the barcodes the max radial of which is greater
        or equal to the distance from the soma to the target.

        Args:
            input_data (dict): The input data parameters.
            random_generator (numpy.random.Generator): The random number generator to use.

        Returns:
            Barcode: The topology barcode.
        """
        target_distance = self.params["distance_soma_target"]

        persistence = sample.ph(
            barcodes_greater_than_distance(input_data["persistence_diagram"], target_distance),
            random_generator,
        )

        if self.params["barcode_scaling"]:
            persistence = scale_barcode(persistence, target_distance)

        return persistence

    def initialize(self):
        """TMD basic grower of an apical tree based on path distance.

        Initializes the tree grower and computes the apical distance using the input barcode.
        """
        stop_criteria, n_sections = super().initialize()
        stop_criteria["target_id"] = self.params["target_id"]
        return stop_criteria, n_sections

    def get_stop_criteria(self, current_section):
        """Get stop criteria.

        Use the stop criteria of the parent class with the additional information
        of the target_id that is assigned to the tree and the max_target_distance for
        calculating the magnitude of the attraction field generated by the target.
        """
        stop1, stop2 = super().get_stop_criteria(current_section)
        stop1["target_id"] = stop2["target_id"] = self.params["target_id"]
        return stop1, stop2

    def bifurcate(self, current_section):
        """When the section bifurcates two new sections need to be created.

        This method computes from the current state the data required for the
        generation of two new sections and returns the corresponding dictionaries.
        """
        self.barcode.remove_bif(current_section.stop_criteria["TMD"].bif_id)
        ang = self.barcode.angles[current_section.stop_criteria["TMD"].bif_id]

        dir1, type1, dir2, type2 = _colonization_split_with_target_influence(
            current_section, ang, self.params, self.context
        )

        first_point = np.array(current_section.last_point)

        stop1, stop2 = self.get_stop_criteria(current_section)

        return (
            section_data(dir1, first_point, stop1, type1),
            section_data(dir2, first_point, stop2, type2),
        )
