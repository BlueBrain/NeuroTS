""" Distribution configuration for morphsynthesis
"""
import imp

from setuptools import find_packages, setup


VERSION = imp.load_source("tns.version", "tns/version.py").VERSION


setup(
    version= VERSION,
    description='TNS= synthesis of artificial neurons using their topological profiles package',
    author='Lida Kanari',
    author_email='lida.kanari@epfl.ch',
    install_requires=[
        'matplotlib>=1.3.1',
        'morphio>=2.0.0',
        'neurom>=1.4.7',
        'tmd>=2.0.4',
        'enum34>=1.0.4',
        'scipy>=0.13.3',
        'numpy>=1.15.0',
    ],
    packages=find_packages(),
    license='BSD',
    scripts=[],
    name='tns',
    include_package_data=True,
)
