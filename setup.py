"""Setup for the NeuroTS package."""

# Copyright (C) 2021-2024  Blue Brain Project, EPFL
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from setuptools import find_namespace_packages
from setuptools import setup

reqs = [
    "jsonschema>=3.0.1",
    "importlib-resources>=5; python_version < '3.9'",
    "matplotlib>=3.4",
    "morphio>=3.3.6,<4.0",
    "neurom>=3.0,<4.0",
    "numpy>=1.22.0,<2",
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
    "pytest-cov>=4.1",
    "pytest-html>=3.2",
    "pytest-xdist>=2",
    "pytest>=6.1",
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
    python_requires=">=3.9",
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
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
