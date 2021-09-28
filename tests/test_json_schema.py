import json
import os

from jsonschema import validate

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def test_json_schema():

    with open(os.path.join(_PATH, 'dummy_distribution.json')) as f:
        data = json.load(f)

    validate(data,
             schema={
                 'definitions': {
                     'histogram': {
                         'type': 'object',
                         'additionalProperties': False,
                         'properties': {
                             'data': {
                                 'type': 'object',
                                 'additionalProperties': False,
                                 'properties': {
                                     'bins': {'type': 'array'},
                                     'weights': {'type': 'array'}
                                 }
                             }
                         }
                     },


                     'dendrite': {
                         'type' : 'object',
                         'additionalProperties': False,
                         'properties': {
                             'trunk': {
                                 'type': 'object',
                                 'additionalProperties': False,
                                 'properties': {
                                     'orientation_deviation': {'$ref': '#/definitions/histogram'},
                                     'azimuth': {
                                         '$ref': '#/definitions/uniform_distrib'
                                     }
                                 }
                             },
                             'num_trees': {'type': 'object'},
                             'persistence_diagram': {'type': 'array'},
                             'filtration_metric': {'type': 'string'},
                         }
                     },

                     'norm_distrib': {
                         'type' : 'object',
                         'additionalProperties': False,
                         'properties': {
                             'norm': {
                                 'type': 'object',
                                 'additionalProperties': False,
                                 'properties': {
                                     'mean': {'type': 'number'},
                                     'std': {'type': 'number'},
                                 }
                             }
                         }
                     },

                     'uniform_distrib': {
                         'type' : 'object',
                         'additionalProperties': False,
                         'properties': {
                             'uniform': {
                                 'type': 'object',
                                 'additionalProperties': False,
                                 'properties': {
                                     'min': {'type': 'number'},
                                     'max': {'type': 'number'},
                                 }
                             }
                         }
                     },

                     'diameter': {
                         'type' : 'object',
                         'additionalProperties': True,
                     }
                 },

                 'type': 'object',
                 'properties' : {
                     'soma' : {
                         'type' : 'object',
                         'additionalProperties': False,
                         'properties' : {
                             'size': {'$ref': '#/definitions/norm_distrib'}
                         },
                     },
                     'basal' : {'$ref': '#/definitions/dendrite'},
                     'apical' : {'$ref': '#/definitions/dendrite'},
                     'axon' : {'$ref': '#/definitions/dendrite'},
                     'diameter': {'$ref': '#/definitions/diameter'},
                 },
                 'required': ['soma', 'axon', 'basal', 'apical', 'diameter'],
                 'additionalProperties': False,
             })
