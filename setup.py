""" Distribution configuration for morphsynthesis
"""
import os
from setuptools import setup
from setuptools import find_packages
import pip
from pip.req import parse_requirements
from optparse import Option
from tns.version import VERSION


def parse_reqs(reqs_file):
    ''' parse the requirements '''
    options = Option('--workaround')
    options.skip_requirements_regex = None
    # Hack for old pip versions
    # Versions greater than 1.x have a required parameter "sessions" in
    # parse_requierements
    if pip.__version__.startswith('1.'):
        install_reqs = parse_requirements(reqs_file, options=options)
    else:
        from pip.download import PipSession  # pylint:disable=E0611
        options.isolated_mode = False
        install_reqs = parse_requirements(reqs_file,  # pylint:disable=E1123
                                          options=options,
                                          session=PipSession)

    return [str(ir.req) for ir in install_reqs]

BASEDIR = os.path.dirname(os.path.abspath(__file__))
REQS = parse_reqs(os.path.join(BASEDIR, 'requirements.txt'))

EXTRA_REQS_PREFIX = 'requirements_'
EXTRA_REQS = {}

for file_name in os.listdir(BASEDIR):
    if not file_name.startswith(EXTRA_REQS_PREFIX):
        continue
    base_name = os.path.basename(file_name)
    (extra, _) = os.path.splitext(base_name)
    extra = extra[len(EXTRA_REQS_PREFIX):]
    EXTRA_REQS[extra] = parse_reqs(file_name)

config = {
    'description': 'TNS: synthesis of artificial neurons using their topological profiles package',
    'author': 'Lida Kanari',
    'url': 'https://bitbucket.org/bbp_lida/morphsynthesis',
    'author_email': 'lida.kanari@epfl.ch',
    'install_requires': REQS,
    'extras_require': EXTRA_REQS,
    'packages': find_packages(),
    'license': 'BSD',
    'scripts': [],
    'name': 'tns',
    'include_package_data': True,
}

setup(**config)
