"""Test JSON schema validation."""

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
import json
import os

from jsonschema import validate

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def test_json_schema():

    with open(os.path.join(_PATH, "dummy_distribution.json"), encoding="utf-8") as f:
        data = json.load(f)

    validate(
        data,
        schema={
            "definitions": {
                "histogram": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "data": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {"bins": {"type": "array"}, "weights": {"type": "array"}},
                        }
                    },
                },
                "dendrite": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "trunk": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "orientation_deviation": {"$ref": "#/definitions/histogram"},
                                "absolute_elevation_deviation": {"$ref": "#/definitions/histogram"},
                                "azimuth": {"$ref": "#/definitions/uniform_distrib"},
                            },
                        },
                        "num_trees": {"type": "object"},
                        "persistence_diagram": {"type": "array"},
                        "filtration_metric": {"type": "string"},
                    },
                },
                "norm_distrib": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "norm": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "mean": {"type": "number"},
                                "std": {"type": "number"},
                            },
                        }
                    },
                },
                "uniform_distrib": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "uniform": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "min": {"type": "number"},
                                "max": {"type": "number"},
                            },
                        }
                    },
                },
                "diameter": {
                    "type": "object",
                    "additionalProperties": True,
                },
            },
            "type": "object",
            "properties": {
                "soma": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"size": {"$ref": "#/definitions/norm_distrib"}},
                },
                "basal": {"$ref": "#/definitions/dendrite"},
                "apical": {"$ref": "#/definitions/dendrite"},
                "axon": {"$ref": "#/definitions/dendrite"},
                "diameter": {"$ref": "#/definitions/diameter"},
            },
            "required": ["soma", "axon", "basal", "apical", "diameter"],
            "additionalProperties": False,
        },
    )
