"""Test neurots.astrocyte.section code."""

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

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
import itertools

import numpy as np
from mock import Mock
from numpy import testing as npt

from neurots.astrocyte.section import SectionSpatialGrower
from neurots.generate.tree import SectionParameters

POINT_CLOUD_POINTS = np.array(
    [
        [0.0, 0.0, 0.0],
        [0.1, 0.1, 0.1],
        [0.2, 0.2, 0.2],
        [0.3, 0.3, 0.3],
        [0.5, 0.5, 0.5],
        [0.6, 0.6, 0.6],
    ]
)

SECTION_PARAMETERS = SectionParameters(randomness=0.5, targeting=0.5, scale_prob=1.0, history=0.0)


def _point_cloud():
    point_cloud = Mock(points=POINT_CLOUD_POINTS, remove_hemisphere=Mock())

    values = [
        np.array([0.0, 0.0, 1.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
    ]

    point_cloud.nearest_neighbor_direction = Mock(side_effect=itertools.cycle(values))

    return point_cloud


class MockMorphologyPoints:
    def __init__(self):
        self._points = np.array([[0.0, 1.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

    def append(self, point):
        self._points = np.vstack((self._points, point))

    @property
    def data(self):
        return self._points


def _spatial_context():
    return Mock(
        point_cloud=_point_cloud(),
        collision_handle=Mock(return_value=False),
        morphology_points=MockMorphologyPoints(),
    )


def _create_section_spatial_grower(process_type):
    start_point = np.array([0.0, 1.0, 2.0])
    direction = np.array([0.0, 1.0, 0.0])

    parent = Mock()

    step_size_distribution = Mock()
    # draw positive will cycle between 0.1, and 0.2
    step_size_distribution.draw_positive = Mock(side_effect=itertools.cycle([0.1, 0.2]))
    step_size_distribution.params = {"mean": 0.1, "std": 0.001}

    return SectionSpatialGrower(
        parent=parent,
        children=[],
        first_point=start_point,
        direction=direction,
        parameters=SECTION_PARAMETERS,
        process=process_type,
        stop_criteria={"TMD": Mock(bif=0.0, term=0.0)},
        step_size_distribution=step_size_distribution,
        pathlength=5.2,
        context=_spatial_context(),
    )


def test_section_spatial_grower__construction():
    grower = _create_section_spatial_grower("major")

    assert grower.process == "major"

    npt.assert_allclose(grower.pathlength, 5.2)
    npt.assert_allclose(grower.params, SECTION_PARAMETERS)
    npt.assert_allclose(grower.direction, [0.0, 1.0, 0.0])

    npt.assert_equal(len(grower.morphology_points.data), 3)

    npt.assert_allclose(grower.history(), [0.0, 0.0, 0.0])
    npt.assert_allclose(grower.last_point, [0.0, 1.0, 2.0])


def test_section_spatial_grower__first_point():
    grower = _create_section_spatial_grower("major")
    grower.first_point()

    expected_point = [0.0, 1.1, 2.0]

    npt.assert_allclose(grower.direction, [0.0, 1.0, 0.0])
    npt.assert_allclose(grower.latest_directions, [[0.0, 1.0, 0.0]])
    npt.assert_allclose(grower.points, [[0.0, 1.0, 2.0], expected_point])

    npt.assert_allclose(
        grower.morphology_points.data,
        [[0.0, 1.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], expected_point],
    )


def test_section_spatial_grower__next_direction():
    grower = _create_section_spatial_grower("major")

    grower.first_point()

    current_point = grower.last_point

    npt.assert_allclose(grower._neighbor_contribution(current_point), [0.0, 0.0, 1.0])

    npt.assert_allclose(grower.history(), [0.0, 1.0, 0.0])
    npt.assert_allclose(grower.next_direction(current_point), [0.0, 1.0, 0.0])


def test_section_spatial_grower__next_point():
    grower = _create_section_spatial_grower("major")
    grower.first_point()
    grower.next()

    expected_next_direction = 0.5 * grower.direction + 0.5 * np.array([0.0, 0.0, 1.0])
    expected_next_direction /= np.linalg.norm(expected_next_direction)

    expected_next_point = np.array([0.0, 1.1, 2.0]) + 0.2 * expected_next_direction

    npt.assert_allclose(grower.latest_directions, [[0.0, 1.0, 0.0], expected_next_direction])

    npt.assert_allclose(grower.points, [[0.0, 1.0, 2.0], [0.0, 1.1, 2.0], expected_next_point])

    npt.assert_allclose(
        grower.morphology_points.data,
        [
            [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 1.1, 2.0],
            expected_next_point,
        ],
    )

    npt.assert_allclose(grower.pathlength, 0.2 + 0.1 + 5.2)
