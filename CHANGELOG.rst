Changelog
=========

Version 2.5.0
-------------

Improvements
~~~~~~~~~~~~
- Update NeuroM dependency to version 3


Version 2.4.5
-------------

Bug Fixes
~~~~~~~~~
- Fix edge case for astrocyte target grower

Improvements
~~~~~~~~~~~~
- Use random generator in morphmath.bifurcation.random()
- Improve extract_input.from_diameter.model


Version 2.4.4
-------------

Improvements
~~~~~~~~~~~~

- Update NeuroM requirements

Version 2.4.3
-------------

New Features
~~~~~~~~~~~~

- Make astrocyte grower RandomState rng consistent with global

Version 2.4.2
-------------

New Features
~~~~~~~~~~~~

- Use an instance of a numpy random generator instead of global numpy.random

Version 2.4.1
-------------

Improvements
~~~~~~~~~~~~

- Improve JSON schemas and add them in the documentation

Version 2.4.0
-------------

New Features
~~~~~~~~~~~~
- Compatibility for NeuroM>=2.1.1
- Pass the context to the modify function

Version 2.3.3
-------------

New Features
~~~~~~~~~~~~
- Compatibility for NeuroM v2

Version 2.3.2
-------------

New Features
~~~~~~~~~~~~
- Bump morphio

Version 2.3.1
-------------

New Features
~~~~~~~~~~~~
- Remove enum-compat from requirements
- Add absolute distribution to trunk orientation
- Can now diametrize only a subset of neurite types
- Add grower for axon trunks

Version 2.3.0
-------------

New Features
~~~~~~~~~~~~
- Store apical section IDs into the diametrizer parameters
- Store the ID of section containing the apical point

Version 2.2.8
-------------

New Features
~~~~~~~~~~~~
- Add doc generation
- Improve doc

Version 2.2.7
-------------

Bug Fixes
~~~~~~~~~
- Compute persistence length correctly

Version 2.2.6
-------------

Bug Fixes
~~~~~~~~~
- Fix apical point detection
