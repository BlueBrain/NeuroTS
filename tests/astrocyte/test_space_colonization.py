"""Test neurots.astrocyte.space_colonization code."""

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

# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
import itertools

import numpy as np
from mock import Mock
from mock import patch
from numpy import testing as npt

from neurots.astrocyte import space_colonization as tested

PCLOUD_POINTS = np.array(
    [
        [0.0, 0.0, 0.0],
        [0.1, 0.1, 0.1],
        [0.2, 0.2, 0.2],
        [0.3, 0.3, 0.3],
        [0.5, 0.5, 0.5],
        [0.6, 0.6, 0.6],
    ]
)


def _point_cloud():
    point_cloud = Mock(points=PCLOUD_POINTS, remove_hemisphere=Mock())

    values = [
        np.array([0.0, 0.0, 1.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),
    ]

    point_cloud.nearest_neighbor_direction = Mock(side_effect=itertools.cycle(values))

    ids = [np.array([0, 1, 2]), np.array([1, 2])]

    point_cloud.ball_query = Mock(side_effect=itertools.cycle(ids))

    return point_cloud


def test_majorize():
    process = "secondary"

    stop = Mock()
    stop.expected_maximum_length.return_value = np.inf

    target_distance = None

    result = tested._majorize_process(process, stop, target_distance)
    assert result == "secondary"

    stop.expected_maximum_length.return_value = 100.0
    target_distance = 90.0

    result = tested._majorize_process(process, stop, target_distance)
    assert result == "major"

    target_distance = 120.0
    result = tested._majorize_process(process, stop, target_distance)
    assert result == "secondary"


def test_repulsion():
    point = np.zeros(3)

    points = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 2.0], [0.0, 0.0, 3.0]])

    vectors = points - point

    result = tested._repulsion(points[:1], point, 1.0)
    expected = vectors[0] * np.exp(-1)
    npt.assert_allclose(result, expected)

    result = tested._repulsion(points[:1], point, 0.5)
    expected = vectors[0] * np.exp(-2.0)
    npt.assert_allclose(result, expected)

    result = tested._repulsion(points[1:2], point, 1.0)
    expected = 0.5 * vectors[1] * np.exp(-1.0 * 2.0)
    npt.assert_allclose(result, expected)

    result = tested._repulsion(points[1:2], point, 0.5)
    expected = 0.5 * vectors[1] * np.exp(-2.0 * 2.0)
    npt.assert_allclose(result, expected)

    result = tested._repulsion(points, point, 0.5)
    expected = (
        vectors[0] * np.exp(-2.0)
        + vectors[1] * np.exp(-2.0 * 2.0) / 2.0
        + vectors[2] * np.exp(-2.0 * 3.0) / 3.0
    ) / 3.0
    npt.assert_allclose(result, expected)


def test_fallback_strategy():
    repulsion = np.array([0.0, 1.0, 2.0])

    mock_dir1 = np.array([1.0, 0.0, 0.0])
    mock_dir2 = np.array([0.0, 1.0, 0.0])

    with patch(
        "neurots.astrocyte.space_colonization.directional",
        return_value=(mock_dir1.copy(), mock_dir2.copy()),
    ):
        section_direction = np.array([0.0, 0.0, 1.0])

        dir1, dir2 = tested._fallback_strategy(section_direction, None, repulsion)

        expected_dir1 = section_direction - repulsion
        expected_dir1 /= np.linalg.norm(expected_dir1)

        npt.assert_allclose(dir1, expected_dir1)

        expected_dir2 = mock_dir2 - repulsion
        expected_dir2 /= np.linalg.norm(expected_dir2)
        npt.assert_allclose(dir2, expected_dir2)


def test_colonization_strategy_secondary():
    vectors = np.array(
        [
            [0.14525965, 0.18989378, 0.73957937],
            [0.72947892, 0.28593541, 0.23994719],
            [0.51646674, 0.20958965, 0.25134127],
        ]
    )

    repulsion = np.array([0.0, 1.0, 2.0])

    dir1, dir2 = tested._colonization_strategy_secondary(vectors, repulsion)

    vecs = vectors - repulsion
    lengths = np.linalg.norm(vecs, axis=1)

    smallest_length_id = np.argmin(lengths)
    expected_dir1 = vecs[smallest_length_id] / lengths[smallest_length_id]
    npt.assert_allclose(dir1, expected_dir1)

    uvecs = vecs / lengths[:, None]

    largest_angle_id = np.argmin(uvecs.dot(dir1))
    expected_dir2 = uvecs[largest_angle_id]

    npt.assert_allclose(dir2, expected_dir2)


def test_colonization_strategy_primary():
    vectors = np.array(
        [
            [0.14525965, 0.18989378, 0.73957937],
            [0.72947892, 0.28593541, 0.23994719],
            [0.51646674, 0.20958965, 0.25134127],
        ]
    )

    repulsion = np.array([0.0, 1.0, 2.0])
    direction = np.array([0.0, 0.0, 1.0])

    dir1, dir2 = tested._colonization_strategy_primary(direction, vectors, repulsion)

    vecs = vectors - repulsion
    lengths = np.linalg.norm(vecs, axis=1)

    expected_dir1 = direction - repulsion
    expected_dir1 /= np.linalg.norm(expected_dir1)

    npt.assert_allclose(dir1, expected_dir1)

    uvecs = vecs / lengths[:, None]

    largest_angle_id = np.argmin(uvecs.dot(dir1))
    expected_dir2 = uvecs[largest_angle_id]

    npt.assert_allclose(dir2, expected_dir2)


def _section(process_type):
    mock = Mock()
    mock.direction = np.array([1.0, 0.0, 0.0])
    mock.last_point = np.array([0.5, 0.5, 0.5])
    mock.segment_length = 0.1
    mock.kill_distance = 1.0
    mock.influence_distance = 2.0

    mock.process = process_type

    mock.step_size_distribution = Mock(params={"mean": 0.1, "std": 0.001})

    mock.stop_criteria = {"max_target_distance": 1.0, "TMD": None, "target_id": 3}
    return mock


def test_colonization_split():
    section = _section("major")
    parameters = {"step_size": {"norm": {"mean": 1.0}}}

    context = Mock(
        point_cloud=Mock(points=np.array([[0.2, 0.3, 0.4], [0.5, 0.6, 0.7]])),
        morphology_points=Mock(data=np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])),
    )
    point_cloud = context.point_cloud

    module = "neurots.astrocyte.space_colonization."

    with patch(module + "_repulsion") as repulsion, patch(
        module + "upper_half_ball_query"
    ) as half_ball_query, patch(module + "_fallback_strategy") as fallback_strategy, patch(
        module + "_colonization_strategy_primary"
    ) as primary_strategy, patch(
        module + "_colonization_strategy_secondary"
    ) as secondary_strategy:
        repulsion.return_value = np.array([3.0, 2.0, 1.0])
        half_ball_query.return_value = []

        # not enough seed points will trigger the fallback strategy
        point_cloud.partial_ball_query.return_value = np.array([0], dtype=int)
        point_cloud.upper_half_ball_query.return_value = np.array([0], dtype=int)

        fallback_strategy.return_value = (
            np.array([0.0, 0.0, 1.0]),
            np.array([1.0, 0.0, 0.0]),
        )

        # for both major
        section.process = "major"
        dir1, typ1, dir2, typ2 = tested._colonization_split(section, None, parameters, context)

        npt.assert_allclose(dir1, [0, 0, 1])
        npt.assert_allclose(dir2, [1, 0, 0])

        assert typ1 == "major"
        assert typ2 == "secondary"

        # and secondary process types
        section.process = "secondary"
        dir1, typ1, dir2, typ2 = tested._colonization_split(section, None, parameters, context)

        npt.assert_allclose(dir1, [0, 0, 1])
        npt.assert_allclose(dir2, [1, 0, 0])

        assert typ1 == "secondary"
        assert typ2 == "secondary"

        # 2 or more point ids and a major section will not trigger the fallback
        point_cloud.partial_ball_query.return_value = np.array([0, 1], dtype=int)
        point_cloud.upper_half_ball_query.return_value = np.array([0, 1], dtype=int)

        # major triggers primary strategy
        section.process = "major"
        primary_strategy.return_value = (
            np.array([0.0, 1.0, 0.0]),
            np.array([-1.0, 0.0, 0.0]),
        )

        dir1, typ1, dir2, typ2 = tested._colonization_split(section, None, parameters, context)

        npt.assert_allclose(dir1, [0, 1, 0])
        npt.assert_allclose(dir2, [-1, 0, 0])

        assert typ1 == "major"
        assert typ2 == "secondary"

        # secondary type triggers secondary strategy
        section.process = "secondary"
        secondary_strategy.return_value = (
            np.array([0.0, 0.0, 1.0]),
            np.array([0.0, 0.0, -1.0]),
        )

        dir1, typ1, dir2, typ2 = tested._colonization_split(section, None, parameters, context)

        npt.assert_allclose(dir1, [0, 0, 1])
        npt.assert_allclose(dir2, [0, 0, -1])

        assert typ1 == "secondary"
        assert typ2 == "secondary"

        # finally if for any reason the strategies return identical directions
        # the dirs are recalculated using the fallback strategy
        secondary_strategy.return_value = (
            np.array([0.0, 0.0, 1.0]),
            np.array([0.0, 0.0, 1.0]),
        )

        dir1, typ1, dir2, typ2 = tested._colonization_split(section, None, parameters, context)

        npt.assert_allclose(dir1, [0, 0, 1])
        npt.assert_allclose(dir2, [1, 0, 0])

        assert typ1 == "secondary"
        assert typ2 == "secondary"


def test_add_attraction_bias():
    target_point = np.array([0.0, 0.0, 100.0])
    current_point = np.array([0.0, 0.0, 0.0])

    def attraction_function(x):
        return 1.0 - x

    max_target_distance = 100.0

    direction = np.array([1.0, 0.0, 0.0])

    new_direction = tested._add_attraction_bias(
        current_point, target_point, max_target_distance, direction, attraction_function
    )

    npt.assert_allclose(new_direction, direction)

    current_point = np.array([0.0, 0.0, 99.99999])

    new_direction = tested._add_attraction_bias(
        current_point, target_point, max_target_distance, direction, attraction_function
    )

    # super close to target -> direction to target only
    npt.assert_allclose(new_direction, [0.0, 0.0, 1.0], atol=1e-6)


def test_colonization_split_with_target_influence():
    parameters = {
        "bias": 1.0,
        "distance_soma_target": 1.0,
        "step_size": {"norm": {"mean": 1.0}},
    }

    section = _section("major")
    section.target = Mock(available=True, xyz=np.array([2.0, 2.0, 2.0]))

    endfeet = Mock()
    endfeet.active = np.ones(5, dtype=bool)
    endfeet.points = np.random.random((5, 3))

    point_cloud = None
    context = Mock(endfeet_targets=endfeet, point_cloud=point_cloud)

    module = "neurots.astrocyte.space_colonization."

    with patch(module + "_colonization_split") as mock_colonization_split, patch(
        module + "in_squared_proximity"
    ) as mock_in_squared_proximity, patch(
        module + "_add_attraction_bias"
    ) as mock_add_attraction_bias, patch(
        module + "_majorize_process"
    ) as mock_majorize_process:
        mock_colonization_split.return_value = (
            np.array([0.0, 0.0, 1.0]),
            None,
            np.array([1.0, 0.0, 0.0]),
            None,
        )

        target_id = section.stop_criteria["target_id"]
        # if there are not active endfeet the space colonization directions are returned
        endfeet.active[target_id] = False

        dir1, typ1, dir2, typ2 = tested._colonization_split_with_target_influence(
            section, None, parameters, context
        )

        npt.assert_allclose(dir1, [0.0, 0.0, 1.0])
        npt.assert_allclose(dir2, [1.0, 0.0, 0.0])

        assert typ1 == "major"
        assert typ2 == "secondary"

        endfeet.active[target_id] = True

        # if point in proximity of target change process type to endfoot
        # the dir2 will be the direction to the target
        mock_in_squared_proximity.return_value = True

        dir1, typ1, dir2, typ2 = tested._colonization_split_with_target_influence(
            section, None, parameters, context
        )

        npt.assert_allclose(dir1, [0.0, 0.0, 1.0])

        expected_direction = endfeet.points[target_id] - section.last_point
        expected_direction /= np.linalg.norm(expected_direction)
        npt.assert_allclose(dir2, expected_direction)

        assert typ1 == "major"
        assert typ2 == "endfoot"

        # target is deactivated when an endfoot is assigned to it
        assert not endfeet.active[target_id]

        # if point not in proximity of the target and the section is
        # of major type, then attraction bias is added
        mock_in_squared_proximity.return_value = False
        section.process = "major"
        endfeet.active[target_id] = True

        mock_add_attraction_bias.return_value = np.array([-1.0, 0.0, 0.0])

        dir1, typ1, dir2, typ2 = tested._colonization_split_with_target_influence(
            section, None, parameters, context
        )

        npt.assert_allclose(dir1, [-1.0, 0.0, 0.0])
        npt.assert_allclose(dir2, [1.0, 0.0, 0.0])

        assert typ1 == "major"
        assert typ2 == "secondary"

        # if point not in proximity of the target and the section is
        # of not major type, then the process type is majorized

        section.process = "secondary"
        mock_majorize_process.return_value = "major"

        dir1, typ1, dir2, typ2 = tested._colonization_split_with_target_influence(
            section, None, parameters, context
        )

        npt.assert_allclose(dir1, [0.0, 0.0, 1.0])
        npt.assert_allclose(dir2, [1.0, 0.0, 0.0])

        assert typ1 == "major"
        assert typ2 == "secondary"
