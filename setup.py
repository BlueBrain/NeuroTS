""" Distribution configuration for morphsynthesis
"""
import imp

from setuptools import find_packages, setup


VERSION = imp.load_source("neurots.version", "neurots/version.py").VERSION

doc_reqs = [
    "m2r2",
    "sphinx",
    "sphinx-bluebrain-theme",
    "sphinx-jsonschema",
]

test_reqs = [
    "mock",
    "morph-tool>=0.1.12",
    "pytest",
    "pytest-cov",
    "pytest-html",
    "pytest-xdist",
    "tqdm",
]

setup(
    name='NeuroTS',
    author='Lida Kanari',
    author_email='lida.kanari@epfl.ch',
    version=VERSION,
    description='Synthesis of artificial neurons using their topological profiles package',
    url="https://bbpteam.epfl.ch/documentation/projects/neurots",
    project_urls={
        "Tracker": "https://bbpteam.epfl.ch/project/issues/projects/CELLS/issues",
        "Source": "https://bbpgitlab.epfl.ch/neuromath/NeuroTS",
    },
    license='BSD',
    install_requires=[
        'matplotlib>=1.3.1',
        'tmd>=2.0.8',
        'morphio>=3.0,<4.0',
        "neurom>=3.0,<4.0",
        'scipy>=0.13.3',
        'numpy>=1.15.0',
        'jsonschema>=3.0.1',
    ],
    extras_require={
        "docs": doc_reqs,
        "test": test_reqs,
    },
    python_requires='>=3.6',
    packages=find_packages(include=["neurots*"]),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
