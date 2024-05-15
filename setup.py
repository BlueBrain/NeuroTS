"""Setup for the NeuroTS package."""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path

from setuptools import find_namespace_packages
from setuptools import setup

reqs = [
    "jsonschema>=3.0.1",
    "importlib-resources>=5; python_version < '3.9'",
    "matplotlib>=3.4",
    "morphio>=3.3.6,<4.0",
    "neurom>=3.0,<4.0",
    "numpy>=1.22.0",
    "packaging>=20",
    "scipy>=1.6",
    "tmd>=2.3.0",
    "diameter-synthesis>=0.5.4",
]

doc_reqs = [
    "docutils<0.21",  # Temporary fix for m2r2
    "m2r2",
    "sphinx",
    "sphinx-bluebrain-theme",
    "sphinx-gallery",
    "sphinx-jsonschema",
]

test_reqs = [
    "dictdiffer>=0.5",
    "mock>=3",
    "morph-tool>=2.9",
    "pytest>=6",
    "pytest-cov>=3",
    "pytest-html>=2",
    "pytest-xdist>=2",
    "tqdm>=4.8.4",
]

setup(
    name="NeuroTS",
    author="Blue Brain Project, EPFL",
    description="Synthesis of artificial neurons using their topological profiles package.",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://NeuroTS.readthedocs.io",
    project_urls={
        "Tracker": "https://github.com/BlueBrain/NeuroTS/issues",
        "Source": "https://github.com/BlueBrain/NeuroTS",
    },
    license="Apache License 2.0",
    packages=find_namespace_packages(include=["neurots*"]),
    python_requires=">=3.8",
    use_scm_version=True,
    setup_requires=[
        "setuptools_scm",
    ],
    install_requires=reqs,
    extras_require={
        "docs": doc_reqs,
        "test": test_reqs,
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
