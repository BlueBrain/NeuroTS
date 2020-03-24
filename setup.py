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
        'morph-tool>=0.1.12',
        'tmd>=2.0.8',
        'neurom @ git+https://git@github.com/BlueBrain/NeuroM.git@mut_morphio#egg=neurom-2.0.0',
        'enum-compat>=0.0.1',
        'scipy>=0.13.3',
        'numpy>=1.15.0',
        'jsonschema>=3.0.1',
    ],
    packages=find_packages(),
    license='BSD',
    scripts=[],
    name='tns',
    include_package_data=True,
)
