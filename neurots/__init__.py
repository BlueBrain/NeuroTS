"""NeuroTS package.

Synthesis of artificial neurons using their topological profiles package.
"""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

import importlib.metadata

from neurots.astrocyte.grower import AstrocyteGrower  # noqa
from neurots.generate.grower import NeuronGrower  # noqa
from neurots.utils import NeuroTSError  # noqa

__version__ = importlib.metadata.version("NeuroTS")
