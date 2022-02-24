"""Distribution configuration for the NeuroTS package."""

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

from setuptools import find_packages
from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    README = f.read()

reqs = [
    "jsonschema>=3.0.1",
    "matplotlib>=1.3.1",
    "morphio>=3.0,<4.0",
    "neurom>=3.0,<4.0",
    "numpy>=1.15.0",
    "scipy>=1.6",
    "tmd>=2.0.8",
]

doc_reqs = [
    "m2r2",
    "sphinx",
    "sphinx-bluebrain-theme",
    "sphinx-gallery",
    "sphinx-jsonschema",
]

test_reqs = [
    "diameter-synthesis>=0.4",
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
    description="Synthesis of artificial neurons using their topological profiles package",
    long_description=README,
    long_description_content_type="text/markdown",
    license="GPLv3",
    url="https://github.com/BlueBrain/NeuroTS",
    project_urls={
        "Tracker": "https://github.com/BlueBrain/NeuroTS/issues",
        "Source": "https://github.com/BlueBrain/NeuroTS",
    },
    install_requires=reqs,
    extras_require={
        "docs": doc_reqs,
        "test": test_reqs,
    },
    tests_require=test_reqs,
    python_requires=">=3.8",
    use_scm_version=True,
    setup_requires=[
        "setuptools_scm",
    ],
    packages=find_packages(include=["neurots*"]),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
