""" Distribution configuration for morphsynthesis
"""
import imp

from setuptools import find_packages, setup


VERSION = imp.load_source("tns.version", "tns/version.py").VERSION

doc_reqs = [
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
    name='TNS',
    author='Lida Kanari',
    author_email='lida.kanari@epfl.ch',
    version=VERSION,
    description='Synthesis of artificial neurons using their topological profiles package',
    url="https://bbpteam.epfl.ch/documentation/projects/tns",
    project_urls={
        "Tracker": "https://bbpteam.epfl.ch/project/issues/projects/CELLS/issues",
        "Source": "ssh://bbpcode.epfl.ch/molecularsystems/TNS",
    },
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
    packages=find_packages(),
    license='BSD',
    scripts=[],
    include_package_data=True,
)
