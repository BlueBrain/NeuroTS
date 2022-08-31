![NeuroTS Logo](docs/source/logo/BBP-NeuroTS.jpg)

[![Version](https://img.shields.io/pypi/v/neurots)](https://github.com/BlueBrain/NeuroTS/releases)
[![Build status](https://github.com/BlueBrain/NeuroTS/actions/workflows/run-tox.yml/badge.svg?branch=main)](https://github.com/BlueBrain/NeuroTS/actions)
[![Codecov.io](https://codecov.io/github/BlueBrain/NeuroTS/coverage.svg?branch=main)](https://codecov.io/github/BlueBrain/NeuroTS?branch=main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/License-GPLv3-blue)](https://github.com/BlueBrain/NeuroTS/blob/main/LICENSE.txt)
[![Documentation status](https://readthedocs.org/projects/neurots/badge/?version=latest)](https://neurots.readthedocs.io/)
[![DOI](https://img.shields.io/badge/DOI-10.1016/j.celrep.2022.110586-blue)](https://doi.org/10.1016/j.celrep.2022.110586)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/BlueBrain/NeuroTS/main?labpath=examples%2Fexplore_example_results.ipynb)


# NeuroTS

Computational generation of artificial neuronal trees based on the topology of reconstructed cells and their
statistical properties.

## Main usage

Neuronal morphologies provide the foundation for the electrical behavior of neurons, the connectomes they form, and the dynamical properties of the brain. Comprehensive neuron models are essential for defining cell types, discerning their functional roles, and investigating brain disease related dendritic alterations. However, a lack of understanding of the principles underlying neuron morphologies has hindered attempts to computationally synthesize morphologies for decades. We introduce a synthesis algorithm based on a topological descriptor of neurons, which enables the rapid digital reconstruction of entire brain regions from few reference cells. This topology-guided synthesis (NeuroTS) generates dendrites that are statistically similar to biological reconstructions in terms of morpho-electrical and connectivity properties and offers a significant opportunity to investigate the links between neuronal morphology and brain function across different spatio-temporal scales.

NeuroTS can be used for the creation of neuronal morphologies from biological reconstructions. The user needs to extract the distributions of topological and statistical properties using the software in order to create the necessary synthesis inputs. Examples of parameters and distributions can be found in the [Parameters and distributions](https://neurots.readthedocs.io/en/stable/params_and_distrs.html) page of the doc.

Once the `input_parameters` and `input_distributions` have been defined, then NeuroTS can generate one or multiple cells based on the respective inputs. The generated cells can be saved in a variety of file formats (SWC, ASC, H5) so that they can be analyzed and visualized by a variety of different software packages. You can find examples on how to extract distributions, generate cells and run basic validations below.

## Examples

We provide some basic examples to showcase the basic functionality of ``NeuroTS``:
* synthesize a single neuron from a basic set of inputs
* synthesize many neurons with the same input parameters and distributions
* synthesize a single neuron with its diameters using a simple method
* synthesize a single neuron with its diameters using an external diametrizer
* extract parameters and distributions that can be used as synthesis inputs

All the scripts of these examples and the required input data are located in the `examples` directory of the repository.

More information can be found in [Examples](https://neurots.readthedocs.io/en/stable/examples/index.html) page of the doc.


## Installation

It is recommended to install ``NeuroTS`` using [pip](https://pip.pypa.io/en/stable/):

```bash
pip install neurots
```

## Citation

When you use the ``NeuroTS`` software or method for your research, we ask you to cite the publication associated to this repository (use the `Cite this repository` button on the [main page](https://github.com/BlueBrain/NeuroTS) of the code).

## Funding & Acknowledgment

The development of this software was supported by funding to the Blue Brain Project, a research center of the École polytechnique fédérale de Lausanne (EPFL), from the Swiss government’s ETH Board of the Swiss Federal Institutes of Technology.

For license and authors, see `LICENSE.txt` and `AUTHORS.md` respectively.

Copyright © 2022 Blue Brain Project/EPFL
