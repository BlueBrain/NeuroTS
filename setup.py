""" Distribution configuration for morphsynthesis
"""
import os
from setuptools import setup
from setuptools import find_packages
import imp
import pip


VERSION = imp.load_source("tns.version", "tns/version.py").VERSION

config = {
    'version': VERSION,
    'description': 'TNS: synthesis of artificial neurons using their topological profiles package',
    'author': 'Lida Kanari',
    'author_email': 'lida.kanari@epfl.ch',
    'install_requires': [
        'matplotlib>=1.3.1',
        'morphio>=2.0.0',
        'neurom>=1.4.7',
        'tmd>=1.0.0',
        'enum34>=1.0.4',
        'scipy>=0.13.3',
        'numpy>=1.8.0',
        'morphio<=2.0.0',
    ],
    'dependency_links': [
        'git+ssh://bbpcode.epfl.ch/molecularsystems/TMD#egg=tmd-1.0.0',
    ],
    'packages': find_packages(),
    'license': 'BSD',
    'scripts': [],
    'name': 'tns',
    'include_package_data': True,
}

setup(**config)
