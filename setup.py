"""Setup for the NeuroTS package."""

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

from pathlib import Path

from setuptools import find_namespace_packages
from setuptools import setup

reqs = [
    "jsonschema>=3.0.1",
    "matplotlib>=1.3.1",
    "morphio>=3.0,<4.0",
    "neurom>=3.0,<4.0",
    "numpy>=1.15.0",
    "scipy>=1.6",
    "tmd>=2.2.0",
]

doc_reqs = [
    "m2r2",
    "sphinx",
    "sphinx-bluebrain-theme",
    "sphinx-gallery",
    "sphinx-jsonschema",
]

test_reqs = [
    "diameter-synthesis>=0.5.0",
    "dictdiffer",
    "mock",
    "morph-tool>=0.1.12",
    "numpy>=1.22",
    "pytest",
    "pytest-cov",
    "pytest-html",
    "pytest-xdist",
    "tqdm",
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
    license="GNU General Public License v3.0",
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
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    include_package_data=True,
)
