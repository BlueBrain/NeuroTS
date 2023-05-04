# Changelog

## [3.3.2](https://github.com/BlueBrain/NeuroTS/compare/3.3.1..3.3.2)

> 4 May 2023

### Fixes

- Raise clear errors for empty angles (Adrien Berchet - [#65](https://github.com/BlueBrain/NeuroTS/pull/65))

## [3.3.1](https://github.com/BlueBrain/NeuroTS/compare/3.3.0..3.3.1)

> 13 March 2023

### Fixes

- Convert apical_sections to new id (Alexis Arnaudon - [#60](https://github.com/BlueBrain/NeuroTS/pull/60))

## [3.3.0](https://github.com/BlueBrain/NeuroTS/compare/3.2.0..3.3.0)

> 13 March 2023

### Build

- Use find_namespace_packages instead of find_packages (Adrien Berchet - [#48](https://github.com/BlueBrain/NeuroTS/pull/48))

### New Features

- new trunk generation algorithm (Alexis Arnaudon - [#49](https://github.com/BlueBrain/NeuroTS/pull/49))
- Rework input validation process (Adrien Berchet - [#52](https://github.com/BlueBrain/NeuroTS/pull/52))

### Fixes

- Report errors in list properly (Adrien Berchet - [#51](https://github.com/BlueBrain/NeuroTS/pull/51))

### Chores And Housekeeping

- Apply Copier template (Adrien Berchet - [#57](https://github.com/BlueBrain/NeuroTS/pull/57))
- Fix language detection (Adrien Berchet - [#50](https://github.com/BlueBrain/NeuroTS/pull/50))

### Refactoring and Updates

- Apply Copier template (Adrien Berchet - [#46](https://github.com/BlueBrain/NeuroTS/pull/46))

### CI Improvements

- Separate job for min_versions to speedup the CI (Adrien Berchet - [#58](https://github.com/BlueBrain/NeuroTS/pull/58))
- Apply Copier template (Adrien Berchet - [#55](https://github.com/BlueBrain/NeuroTS/pull/55))
- Test with minimal versions of dependencies (Adrien Berchet - [#53](https://github.com/BlueBrain/NeuroTS/pull/53))

### General Changes

- Use diameter-synthesis by default (Alexis Arnaudon - [#47](https://github.com/BlueBrain/NeuroTS/pull/47))
- Fix schemas and tests (Adrien Berchet - [#44](https://github.com/BlueBrain/NeuroTS/pull/44))

## [3.2.0](https://github.com/BlueBrain/NeuroTS/compare/3.1.1..3.2.0)

> 26 August 2022

### Documentation Changes

- Update DOI to the final article (Adrien Berchet - [#32](https://github.com/BlueBrain/NeuroTS/pull/32))

### CI Improvements

- Use codespellignorelines files for format job (Adrien Berchet - [#41](https://github.com/BlueBrain/NeuroTS/pull/41))
- Publish wheels on Pypi (Adrien Berchet - [#40](https://github.com/BlueBrain/NeuroTS/pull/40))
- Use commitlint to check PR titles (Adrien Berchet - [#39](https://github.com/BlueBrain/NeuroTS/pull/39))
- Move black, codespell, isort, pycodestyle and pydocstyle from tox to pre-commit (Adrien Berchet - [#29](https://github.com/BlueBrain/NeuroTS/pull/29))

### General Changes

- Bar length warning under skip_validation (lidakanari - [#43](https://github.com/BlueBrain/NeuroTS/pull/43))
- Compatibility of NeuriteType with NeuroM/MorphIO (Alexis Arnaudon - [#42](https://github.com/BlueBrain/NeuroTS/pull/42))
- Update targeting/randomness to paper values (Alexis Arnaudon - [#30](https://github.com/BlueBrain/NeuroTS/pull/30))
- Automatically build MyBinder docker image for each tag (Adrien Berchet - [#28](https://github.com/BlueBrain/NeuroTS/pull/28))
- Update scipy requirement because of QHullError (Adrien Berchet - [#27](https://github.com/BlueBrain/NeuroTS/pull/27))
- Fix warnings (Eleftherios Zisis - [#25](https://github.com/BlueBrain/NeuroTS/pull/25))
- Update build-system (Eleftherios Zisis - [#26](https://github.com/BlueBrain/NeuroTS/pull/26))
- Explicitely states where the examples and related data are located (Adrien Berchet - [#24](https://github.com/BlueBrain/NeuroTS/pull/24))
- Remove useless installation of several packages in Github CI (Adrien Berchet - [#23](https://github.com/BlueBrain/NeuroTS/pull/23))
- Setup MyBinder (Adrien Berchet - [#22](https://github.com/BlueBrain/NeuroTS/pull/22))

## [3.1.1](https://github.com/BlueBrain/NeuroTS/compare/3.1.0..3.1.1)

> 2 March 2022

### General Changes

- Setup CodeCov (Adrien Berchet - [#20](https://github.com/BlueBrain/NeuroTS/pull/20))

<!-- auto-changelog-above -->

## [3.1.0](https://github.com/BlueBrain/NeuroTS/compare/3.0.1..3.1.0)

> 1 March 2022

- Update README.md (alex4200 - [#18](https://github.com/BlueBrain/NeuroTS/pull/18))
- Remove run time from gallery pages (Adrien Berchet - [#17](https://github.com/BlueBrain/NeuroTS/pull/17))
- Make citation more clear and slightly improve coverage (Adrien Berchet - [#16](https://github.com/BlueBrain/NeuroTS/pull/16))
- Update examples (lidakanari - [#12](https://github.com/BlueBrain/NeuroTS/pull/12))
- Can pass parameters to the external diametrizer (Adrien Berchet - [#13](https://github.com/BlueBrain/NeuroTS/pull/13))
- Update CONTRIBUTING.md (alex4200 - [#11](https://github.com/BlueBrain/NeuroTS/pull/11))
- Improve readme file (lidakanari - [#5](https://github.com/BlueBrain/NeuroTS/pull/5))
- default to use_morphio (Alexis Arnaudon - [#10](https://github.com/BlueBrain/NeuroTS/pull/10))
- Fix banner in doc (alex4200 - [#9](https://github.com/BlueBrain/NeuroTS/pull/9))
- Adding logo for NeuroTS (alex4200 - [#8](https://github.com/BlueBrain/NeuroTS/pull/8))
- Add codespell in lint (Adrien Berchet - [#7](https://github.com/BlueBrain/NeuroTS/pull/7))
- Improve installation section in README (Adrien Berchet - [#4](https://github.com/BlueBrain/NeuroTS/pull/4))
- Fix tests/astrocyte/test_grower.py::test_grow__run test (Adrien Berchet - [#6](https://github.com/BlueBrain/NeuroTS/pull/6))
- Change license and open the sources (Adrien Berchet - [#1](https://github.com/BlueBrain/NeuroTS/pull/1))
- Fix distributions for trunk length feature (Adrien Berchet - [fd5235d](https://github.com/BlueBrain/NeuroTS/commit/fd5235d07e4faab523e7fd8fd18bdb34705e8a22))
- Take into account existing points when adding new trunks with no given orientation (Adrien Berchet - [14e11b2](https://github.com/BlueBrain/NeuroTS/commit/14e11b2095c71c902e1200f6bd4c0944c1ca7afa))
- Fix the parameter schema for the new orientation manager (Adrien Berchet - [a384c1c](https://github.com/BlueBrain/NeuroTS/commit/a384c1c1993a261a08cf46db2547f9cc9e55063f))

## [3.0.1](https://github.com/BlueBrain/NeuroTS/compare/3.0.0..3.0.1)

> 14 October 2021

- Fix MANIFEST.in to package the JSON schemas (Adrien Berchet - [4c2d80c](https://github.com/BlueBrain/NeuroTS/commit/4c2d80cabe27a2e9faac81ca71abf83a3645b667))

## [3.0.0](https://github.com/BlueBrain/NeuroTS/compare/2.5.0..3.0.0)

> 12 October 2021

- Black the code (Adrien Berchet - [59dd107](https://github.com/BlueBrain/NeuroTS/commit/59dd1072546baf55aa58c009812fbda1b747f0cc))
- Refactor and introduce orientation manager (Eleftherios Zisis - [b9bbeeb](https://github.com/BlueBrain/NeuroTS/commit/b9bbeeb3d7a335fedc63006b7d8c2d1e61e6a894))
- Use pytest (Adrien Berchet - [1a790fb](https://github.com/BlueBrain/NeuroTS/commit/1a790fba0d5a93e77c8be47c21d780d61029219b))
- Rename TNS into NeuroTS (Adrien Berchet - [bb08805](https://github.com/BlueBrain/NeuroTS/commit/bb088051517ecc1fdb4bc081471059d156ac0620))

## [2.5.0](https://github.com/BlueBrain/NeuroTS/compare/2.4.5..2.5.0)

> 30 August 2021

- update NeuroM dependency to 3.0.0 (aleksei sanin - [68ed1f7](https://github.com/BlueBrain/NeuroTS/commit/68ed1f7a0cef2bb77503ff45eea38db18d944ba7))

## [2.4.5](https://github.com/BlueBrain/NeuroTS/compare/2.4.4..2.4.5)

> 30 August 2021

- Improve extract_input.from_diameter.model (Adrien Berchet - [e324779](https://github.com/BlueBrain/NeuroTS/commit/e3247794dfe058a2dabd6990bc591b313ed1f2c7))
- Fix edge case for astrocyte target grower (Eleftherios Zisis - [9a06ea3](https://github.com/BlueBrain/NeuroTS/commit/9a06ea33bdf32c4330d90209b6e0924c7415fc39))
- prepare release 2.4.5 (aleksei sanin - [a94e5a5](https://github.com/BlueBrain/NeuroTS/commit/a94e5a568672e896a2dabbb93c6db650371f118d))
- Use random generator in morphmath.bifurcation.random() (Adrien Berchet - [c955380](https://github.com/BlueBrain/NeuroTS/commit/c955380fe75b1843bbe38c2ae0ce45d3c873bea7))

## [2.4.4](https://github.com/BlueBrain/NeuroTS/compare/2.4.3..2.4.4)

> 7 June 2021

- Update NeuroM requirements (Adrien Berchet - [6a56e55](https://github.com/BlueBrain/NeuroTS/commit/6a56e55bc2044da7ef047134bdf8d44bd7eb969e))
- Fix for NeuroM&gt;=2.2 (Adrien Berchet - [6318a26](https://github.com/BlueBrain/NeuroTS/commit/6318a26aac1e6de984f8b4474b6292326181e95a))

## [2.4.3](https://github.com/BlueBrain/NeuroTS/compare/2.4.2..2.4.3)

> 2 June 2021

- Make astrocyte grower RandomState rng consistent with global (Eleftherios Zisis - [fa69154](https://github.com/BlueBrain/NeuroTS/commit/fa69154373018069461534a9e0b579510a0b20ed))

## [2.4.2](https://github.com/BlueBrain/NeuroTS/compare/2.4.1..2.4.2)

> 6 May 2021

- Merge "Use an instance of a numpy random generator instead of global numpy.random" (Alexis Arnaudon - [754d697](https://github.com/BlueBrain/NeuroTS/commit/754d697ce8551595f1668ae3c524e8a73822575f))
- Use an instance of a numpy random generator instead of global numpy.random (Adrien Berchet - [2cbcfe0](https://github.com/BlueBrain/NeuroTS/commit/2cbcfe018abaa158ac16a3ca1c3f17ee424c8db4))

## [2.4.1](https://github.com/BlueBrain/NeuroTS/compare/2.4.0..2.4.1)

> 5 May 2021

- Improve JSON schemas and add them in the documentation (Adrien Berchet - [1760dee](https://github.com/BlueBrain/NeuroTS/commit/1760dee7e743984dd6642085432eacc78c08c72c))

## [2.4.0](https://github.com/BlueBrain/NeuroTS/compare/2.3.3..2.4.0)

> 4 May 2021

- Compat for NeuroM==2.1.1 (Adrien Berchet - [eeeb2da](https://github.com/BlueBrain/NeuroTS/commit/eeeb2dab8b1785947f57e77e287a7f0647f95c95))
- Pass the context to the modify function (Adrien Berchet - [015dbf8](https://github.com/BlueBrain/NeuroTS/commit/015dbf8ef9976870da89ce675fea57d41bb8b797))

## [2.3.3](https://github.com/BlueBrain/NeuroTS/compare/2.3.2..2.3.3)

> 19 April 2021

- fix test for neuromv2 (arnaudon - [f0e87d7](https://github.com/BlueBrain/NeuroTS/commit/f0e87d72c538b56a47b548bee0f2d5b6337e408f))
- Tree -&gt; Section (arnaudon - [3654e87](https://github.com/BlueBrain/NeuroTS/commit/3654e87a8e1ca34a82d90b8f15b6bbf0a914e300))
- release 2.3.3 for neuromv2 (arnaudon - [a332692](https://github.com/BlueBrain/NeuroTS/commit/a332692c6d8561f4fb412914a371ed57cc391457))

## [2.3.2](https://github.com/BlueBrain/NeuroTS/compare/2.3.1..2.3.2)

> 18 March 2021

- bump morphio (arnaudon - [241bcf9](https://github.com/BlueBrain/NeuroTS/commit/241bcf9cde194b5434d6e649d3ca96c99ec5f391))
- bump version (arnaudon - [7ea8e40](https://github.com/BlueBrain/NeuroTS/commit/7ea8e40334987f5805313c6c35db8e4c8a5de4c0))

## [2.3.1](https://github.com/BlueBrain/NeuroTS/compare/2.3.0..2.3.1)

> 16 March 2021

- Add absolute distribution to trunk orientation (Adrien Berchet - [09fa4d8](https://github.com/BlueBrain/NeuroTS/commit/09fa4d83454838033fafb822b84134bd6f9c5ff5))
- Add grower for axon trunks (Adrien Berchet - [986d275](https://github.com/BlueBrain/NeuroTS/commit/986d2759bd6b077678b038043afb3a980471827f))
- Can now diametrize only a subset of neurite types (Adrien Berchet - [50532f7](https://github.com/BlueBrain/NeuroTS/commit/50532f7dc6c490e453b677c173016f2228817536))
- bump version (arnaudon - [a67972b](https://github.com/BlueBrain/NeuroTS/commit/a67972be3eae919c0aa5b7fe5e7d6060f52f631f))
- remove enum-compat (arnaudon - [e22e5de](https://github.com/BlueBrain/NeuroTS/commit/e22e5de5a2c394841844775c7105a2d36ba83d2a))

## [2.3.0](https://github.com/BlueBrain/NeuroTS/compare/2.2.9..2.3.0)

> 12 January 2021

- Improve test coverage and minor cleaning (Adrien Berchet - [1e1f43e](https://github.com/BlueBrain/NeuroTS/commit/1e1f43ee87628119e1da6820f2d643fa1cfce828))
- Store the ID of section containing the apical point (Adrien Berchet - [16cc1ab](https://github.com/BlueBrain/NeuroTS/commit/16cc1ab80ef1db9227df716993c05ca7986ed576))
- Store apical section IDs into the diametrizer parameters (Adrien Berchet - [277b78b](https://github.com/BlueBrain/NeuroTS/commit/277b78b06dbc599377f47637b16cda61f7e3b1b5))

## [2.2.9](https://github.com/BlueBrain/NeuroTS/compare/2.2.8..2.2.9)

> 9 December 2020

## [2.2.8](https://github.com/BlueBrain/NeuroTS/compare/2.2.7..2.2.8)

> 9 December 2020

- Add doc generation (Adrien Berchet - [0852d7c](https://github.com/BlueBrain/NeuroTS/commit/0852d7c89f74b4c95da015a0ad9f0555f1639e62))
- Improve doc (Adrien Berchet - [b1e86be](https://github.com/BlueBrain/NeuroTS/commit/b1e86be33535568314c7f388f5fa942846d6f705))
- Release version 2.2.8 (arnaudon - [0a0bb24](https://github.com/BlueBrain/NeuroTS/commit/0a0bb24db1156e81f202484bac7201c481043b6b))

## [2.2.7](https://github.com/BlueBrain/NeuroTS/compare/2.2.6..2.2.7)

> 4 November 2020

- Compute persistence length correctly (kanari - [86fe018](https://github.com/BlueBrain/NeuroTS/commit/86fe018bf799b3295db5f50d41220aaebbdc20b6))
- Release version 2.2.7 (kanari - [44f1c32](https://github.com/BlueBrain/NeuroTS/commit/44f1c32d24796597366c5a14dcdc9fadccac551f))

## [2.2.6](https://github.com/BlueBrain/NeuroTS/compare/2.2.5..2.2.6)

> 22 October 2020

- Fix apical point detection (Adrien Berchet - [0618ad9](https://github.com/BlueBrain/NeuroTS/commit/0618ad917f42a98b4e20f78c53b18f660fb6805b))

## [2.2.5](https://github.com/BlueBrain/NeuroTS/compare/2.2.4..2.2.5)

> 14 October 2020

- Allow unknown attributes in parameters and allow to skip the validation (Adrien Berchet - [8af8acf](https://github.com/BlueBrain/NeuroTS/commit/8af8acf27e0c39fc65a5593c129f7b0c9e3f3172))

## [2.2.4](https://github.com/BlueBrain/NeuroTS/compare/2.2.3..2.2.4)

> 9 October 2020

- Rename context into context_constraints in tmd_parameters (Adrien Berchet - [3822e49](https://github.com/BlueBrain/NeuroTS/commit/3822e49c6fb81e4e7276fe1edfe8b43b2d4cc8bd))

## [2.2.3](https://github.com/BlueBrain/NeuroTS/compare/2.2.2..2.2.3)

> 7 October 2020

- Update JSON Schema to clean it and add limits (Adrien Berchet - [e37b6ff](https://github.com/BlueBrain/NeuroTS/commit/e37b6ffd879ba209768f45e12338c7ca46b14333))
- Make input parameter bias length unit free (kanari - [c6c41e6](https://github.com/BlueBrain/NeuroTS/commit/c6c41e6d49e8fc8882cddf8271c827700afbd317))
- New release (Adrien Berchet - [f2ea427](https://github.com/BlueBrain/NeuroTS/commit/f2ea42742a5b1db454f5848dc4d66e14d0801418))

## [2.2.2](https://github.com/BlueBrain/NeuroTS/compare/2.2.1..2.2.2)

> 3 August 2020

- Make pylint version compatible and remove morph-tool unnecessary dependency (kanari - [e1e3650](https://github.com/BlueBrain/NeuroTS/commit/e1e36502749694cf6cf0e7544066093bd50a25ce))
- Make version visible + minor clean-up (kanari - [f664d8f](https://github.com/BlueBrain/NeuroTS/commit/f664d8fa5b3b81344bf172e168d57d37b30d683b))
- Release tns version 2.2.2 (kanari - [1325430](https://github.com/BlueBrain/NeuroTS/commit/132543020f93a66449e2b872a90c2813354c4757))

## [2.2.1](https://github.com/BlueBrain/NeuroTS/compare/2.2.0..2.2.1)

> 29 June 2020

- Fix validation schemas paths (Benoît Coste - [bcbff83](https://github.com/BlueBrain/NeuroTS/commit/bcbff834423af7f0d098fe5f9aed123253cecc1c))
- Fix manifest (Benoît Coste - [4ca81a7](https://github.com/BlueBrain/NeuroTS/commit/4ca81a730443022088ab590ab99d8c87e1a7e02c))
- Bump version to v2.2.1 (Benoît Coste - [cd3da5d](https://github.com/BlueBrain/NeuroTS/commit/cd3da5d2783c827e30c894eee875f537cccef465))

## [2.2.0](https://github.com/BlueBrain/NeuroTS/compare/2.0.7..2.2.0)

> 28 June 2020

- Add astrocyte synthesis (Eleftherios Zisis - [fcbf2ec](https://github.com/BlueBrain/NeuroTS/commit/fcbf2ec2687f61b635dfb2c6ca6f5775b15a9f6e))
- Validates JSON files before growth (Benoît Coste - [0feb20c](https://github.com/BlueBrain/NeuroTS/commit/0feb20c3b911144321b4e290251d6a50108e70d4))
- Drop Python 2 support and use Neurom v1 (Benoît Coste - [7318edb](https://github.com/BlueBrain/NeuroTS/commit/7318edb5b38a8cec39aed8f36ec5cf7e14551336))
- Clean up init of TMDAlgo (kanari - [f2766cf](https://github.com/BlueBrain/NeuroTS/commit/f2766cfeea935be181789af41ae733b1ca0bcb1c))
- Replace test astrocyte to fix test (eleftherioszisis - [534ab38](https://github.com/BlueBrain/NeuroTS/commit/534ab3817f85590dab90192bf637b4546abe0f44))
- Make astrocyte synthesis release (Eleftherios Zisis - [2802b55](https://github.com/BlueBrain/NeuroTS/commit/2802b55f499516b8fa6dcaa24ba39515c5a9fee5))

## [2.0.7](https://github.com/BlueBrain/NeuroTS/compare/2.0.6..2.0.7)

> 31 March 2020

- Fix bugs related to apical point (kanari - [43f4ec9](https://github.com/BlueBrain/NeuroTS/commit/43f4ec9829b168022e3fe5481e17f11decf2f811))
- Release tns version 2.0.7 (kanari - [6a45cc2](https://github.com/BlueBrain/NeuroTS/commit/6a45cc296788864ca4a4c3d5db790f996298da7b))

## [2.0.6](https://github.com/BlueBrain/NeuroTS/compare/2.0.4..2.0.6)

> 27 March 2020

- Add alternative apical point definition (kanari - [678cc5e](https://github.com/BlueBrain/NeuroTS/commit/678cc5e148c5f0775df67cc2cad79695795d12f7))
- Revert "morphio -&gt; neurom v2" (arnaudon - [02a171c](https://github.com/BlueBrain/NeuroTS/commit/02a171ca077091fd9c5acc899ae67a602c792101))
- tiny modif in history function to gain speed (Alexis Arnaudon - [6b3cc18](https://github.com/BlueBrain/NeuroTS/commit/6b3cc1877cb8c3c638c74fc6ec83d1a6f0ab25a2))
- Add consistency check and error wanring for selected step-size (kanari - [a81992f](https://github.com/BlueBrain/NeuroTS/commit/a81992f0d5eb6747bb148a114052e6dca6f69d7e))
- Release version 2.0.6 (kanari - [4c3ad06](https://github.com/BlueBrain/NeuroTS/commit/4c3ad065811171fc58af0d9833049b151bbd8dbd))

## [2.0.4](https://github.com/BlueBrain/NeuroTS/compare/2.0.2..2.0.4)

> 13 February 2020

- morphio -&gt; neurom v2 (Alexis Arnaudon - [c48a3d4](https://github.com/BlueBrain/NeuroTS/commit/c48a3d48c03a71cfdcc87d73e34bb74ad5d5a359))
- new release (Alexis Arnaudon - [0c0d352](https://github.com/BlueBrain/NeuroTS/commit/0c0d352031087e4c8b827ebd7baead1a76904f24))

## [2.0.2](https://github.com/BlueBrain/NeuroTS/compare/2.0.0..2.0.2)

> 11 February 2020

- allow for external diametrizer (Alexis Arnaudon - [11157ce](https://github.com/BlueBrain/NeuroTS/commit/11157ce6c4709b506452af6a2cca28da7dce244a))
- Refactor section data and section parameters (Eleftherios Zisis - [0f994ac](https://github.com/BlueBrain/NeuroTS/commit/0f994ac6b05246c4114aba66a3cdef398fc08f40))
- Consistency fixes for input distributions and parameters (kanari - [5cf48ba](https://github.com/BlueBrain/NeuroTS/commit/5cf48ba1c6d9358a84f4191033f14ea9097c1d39))
- Version update (kanari - [f671fba](https://github.com/BlueBrain/NeuroTS/commit/f671fbaaa2e6521f7f2975c45ea0d6e37ffdfa8c))

## [2.0.0](https://github.com/BlueBrain/NeuroTS/compare/1.0.8..2.0.0)

> 28 January 2020

- Removing radial distances based growth, since it is not used for neurons or astrocytes. This will simplify the code and ensure robustness. The metric system will remain for possible future implementation, but it will only support path distances for now. The radial distances are removed because bars are not correctly ordered for the growth, namely start point can be larger than end point. (kanari - [542cfa6](https://github.com/BlueBrain/NeuroTS/commit/542cfa6d11f06616d330625a1957b22604fe048a))
- Fix normalization bug and improve branching direction (kanari - [5c91803](https://github.com/BlueBrain/NeuroTS/commit/5c91803c7064ac4cbb331e45e550216f16715113))
- Clean up code and small corrections (kanari - [f765d40](https://github.com/BlueBrain/NeuroTS/commit/f765d40466a547fd4e08820a52fe0e9350fcc981))
- Changes to correct problems with curation of bifurcation - termination. (kanari - [12952d9](https://github.com/BlueBrain/NeuroTS/commit/12952d9be33b305348e14871a7e2c1a4b1ad3d5e))
- Cleaning and fix small error (kanari - [fc42410](https://github.com/BlueBrain/NeuroTS/commit/fc424109465d66f9686558ce1916c63e695be1b6))
- Clarify - simplify use of barcode in TMD based synthesis (kanari - [3c48c2c](https://github.com/BlueBrain/NeuroTS/commit/3c48c2c0d6c45207ba6ff7b2ee1b0131d334a932))
- Ensure radial - path distances are not mixed (kanari - [a56ec1f](https://github.com/BlueBrain/NeuroTS/commit/a56ec1f1a7ce904c5be8625e4e19e8d28139fac0))
- Create TrunkAlgo tests (Benoît Coste - [5e0cd38](https://github.com/BlueBrain/NeuroTS/commit/5e0cd38ffa673770abb5ad7845145171f3440014))
- Introduce spatial (Benoît Coste - [4be6568](https://github.com/BlueBrain/NeuroTS/commit/4be656814598bb3c820d790c9ddd4dcbf064802e))
- Cleanup of SomaGrower, tests and a consistent interface for the soma points (Eleftherios Zisis - [96e4e58](https://github.com/BlueBrain/NeuroTS/commit/96e4e588b55e952040c9fc30feb5176e6fbda8a1))
- Create input_distributions.py and input_parameters.py (Benoît Coste - [d49c8c8](https://github.com/BlueBrain/NeuroTS/commit/d49c8c8850fd4056d17ba7c4e70bcd0433d756ad))
- Create tests for algorithms (Benoît Coste - [8a1a7f7](https://github.com/BlueBrain/NeuroTS/commit/8a1a7f7d49abe501db0e3ad48e47ddb55e824229))
- Rename SectionGrower::points3D to points (Benoît Coste - [b3d560c](https://github.com/BlueBrain/NeuroTS/commit/b3d560c3e85dddff1b47edaec0b5c80404783bfd))
- Move get_random_point to utils.py and activate a logger (Benoît Coste - [653eb4a](https://github.com/BlueBrain/NeuroTS/commit/653eb4a20042dc04f5db779ac3f56524f54e40b6))
- Use NeuroM v2 (Benoît Coste - [e895783](https://github.com/BlueBrain/NeuroTS/commit/e895783f817802fb268b7a7fb96e0c608cc46588))
- Fix for wrong grid cell id due to floating point accuracy:x (Eleftherios Zisis - [2708b74](https://github.com/BlueBrain/NeuroTS/commit/2708b74b4fefaae03f97d2b30ec0dce3c6ccc0e0))
- Remove empty test file (Benoît Coste - [998edc4](https://github.com/BlueBrain/NeuroTS/commit/998edc4e06bfed81359b85175b4d85e5e147ca4f))
- Correct small errors (kanari - [b84b964](https://github.com/BlueBrain/NeuroTS/commit/b84b964c821dada0dfaa93113efcd5de81144ce0))
- Complete list of possible input algorithms (kanari - [fa9f488](https://github.com/BlueBrain/NeuroTS/commit/fa9f488c3abeaf7f5ba793fde12570c265dd9e3d))
- Fix TMD version (Benoît Coste - [f09c48b](https://github.com/BlueBrain/NeuroTS/commit/f09c48b908ffcf4041488c16b6f9854843d011b8))
- Bumping TNS to v2.0.0 (Benoît Coste - [1d6094c](https://github.com/BlueBrain/NeuroTS/commit/1d6094c7c6fd8639b13c411c642c0f1625f7b119))
- Merge "Ensure radial - path distances are not mixed" (Lida Kanari - [92202b9](https://github.com/BlueBrain/NeuroTS/commit/92202b9020b2465f35aeb7afbf580fa682976196))

## [1.0.8](https://github.com/BlueBrain/NeuroTS/compare/1.0.7..1.0.8)

> 4 March 2019

- Fix bug with latest directions (kanari - [5bedcb7](https://github.com/BlueBrain/NeuroTS/commit/5bedcb7a3ffecc304bc3fe76e1384a92ac29506e))
- Release tns==1.0.8 (Arseny V. Povolotsky - [3bea788](https://github.com/BlueBrain/NeuroTS/commit/3bea788d3e52eb2de72a5c547ab3973eb28cea90))

## [1.0.7](https://github.com/BlueBrain/NeuroTS/compare/1.0.6..1.0.7)

> 26 February 2019

- Fix bugs in diameter models (kanari - [2819a5e](https://github.com/BlueBrain/NeuroTS/commit/2819a5e4bb5c87e4047cf2705505c5f0b4fd93ff))
- Add unit test (Benoît Coste - [8aba5fd](https://github.com/BlueBrain/NeuroTS/commit/8aba5fdbd60a23ef09039a83d8f91733ba28450b))
- Release tns==1.0.7 (Arseny V. Povolotsky - [c2e3bef](https://github.com/BlueBrain/NeuroTS/commit/c2e3bef784d6d24727a151c8b830ce8709f2890c))

## [1.0.6](https://github.com/BlueBrain/NeuroTS/compare/1.0.5..1.0.6)

> 19 February 2019

- Add / correct diameter models, fix relevant tests. (kanari - [4c145fa](https://github.com/BlueBrain/NeuroTS/commit/4c145fa96fc4ee99f7025f0bd72cec01f3757566))
- Fix diameters so that neurite types are properly handled. (kanari - [31c25d5](https://github.com/BlueBrain/NeuroTS/commit/31c25d5fcce819f501e9034f3b0ad89c0caff62f))
- Fix one point soma, default soma is set to contour (kanari - [125bb7f](https://github.com/BlueBrain/NeuroTS/commit/125bb7f6a47d58e6947196b3c5bfe94a452baffd))
- Diameter model keys are section type names (axon, apical, etc.) (Benoît Coste - [8ac935d](https://github.com/BlueBrain/NeuroTS/commit/8ac935d4bbebb76ca9110ef269d0304b716c9faf))
- Add ability to pass contextual information to all growers (Benoît Coste - [79f342f](https://github.com/BlueBrain/NeuroTS/commit/79f342fdf4ca1034845c2ffda00583b2ab767a07))
- AbstractAlgo ctor initialize its arguments (Benoît Coste - [d00f0ad](https://github.com/BlueBrain/NeuroTS/commit/d00f0ade2819b4a6e671ed657977f484e6b1f13a))
- Bump version (Benoît Coste - [20464b3](https://github.com/BlueBrain/NeuroTS/commit/20464b3a23c12bb7e30cda59811606d447e53a39))
- Merge "AbstractAlgo ctor initialize its arguments" (Benoît Coste - [c907e15](https://github.com/BlueBrain/NeuroTS/commit/c907e15b2f0e4543eab1eca6e70ac758a03693ca))
- Merge "Use logging module" (Benoît Coste - [e8b54fe](https://github.com/BlueBrain/NeuroTS/commit/e8b54febd83cc277e765c9d86580a3fa719df111))
- Merge "Add / correct diameter models, fix relevant tests." (Lida Kanari - [7a7fb91](https://github.com/BlueBrain/NeuroTS/commit/7a7fb913c88857b60cf586b7a87a19316a4bffbf))
- Use logging module (Benoît Coste - [3b991ca](https://github.com/BlueBrain/NeuroTS/commit/3b991ca58ca4bd04536027068aaf62d65887d9cd))

## [1.0.5](https://github.com/BlueBrain/NeuroTS/compare/1.0.4..1.0.5)

> 7 February 2019

- Remove Makefile and fix grower (Benoît Coste - [f7d6f3c](https://github.com/BlueBrain/NeuroTS/commit/f7d6f3c32e0e05f9ee3528bd6cc59160d1e2f2f5))
- Neuron generated with 2 neurites have a 1 point soma sphere (Benoît Coste - [9655179](https://github.com/BlueBrain/NeuroTS/commit/9655179c5502470e8766328b868649d87e306b37))
- Release tns==1.0.5 (Arseny V. Povolotsky - [93ff23b](https://github.com/BlueBrain/NeuroTS/commit/93ff23b7fb0aef2395aa4c1366af085ad5a8eb18))
- Merge "Release tns==1.0.4" (Arseniy Povolotskiy - [9ab54fb](https://github.com/BlueBrain/NeuroTS/commit/9ab54fbf12221e74e9017c7ad528c98ea17f3cd5))
- Unpin 'tmd' dependency (Arseny V. Povolotsky - [c0d185b](https://github.com/BlueBrain/NeuroTS/commit/c0d185b7b1791d9c6310a884eef1e10ba6e3d294))

## [1.0.4](https://github.com/BlueBrain/NeuroTS/compare/1.0.3..1.0.4)

> 4 February 2019

- Fixed imports in setup.py (Arseny V. Povolotsky - [1a1e231](https://github.com/BlueBrain/NeuroTS/commit/1a1e2311c861388a31380a36ec42914aee6da4c0))
- Release tns==1.0.4 (Arseny V. Povolotsky - [299eb15](https://github.com/BlueBrain/NeuroTS/commit/299eb151291980cb2cac6d1607f1bcaf3fff85a1))

## [1.0.3](https://github.com/BlueBrain/NeuroTS/compare/1.0.2..1.0.3)

> 4 February 2019

- Cleanup + add some tests (Benoît Coste - [970b75b](https://github.com/BlueBrain/NeuroTS/commit/970b75b985f6ff8f0a7db560e2dd136446cc1a0c))
- Activate tox -e pylint (Benoît Coste - [cf47987](https://github.com/BlueBrain/NeuroTS/commit/cf47987885174243b35d14be30ab6f2957ec1e55))
- Activate tox -e pycodestyle (Benoît Coste - [f276328](https://github.com/BlueBrain/NeuroTS/commit/f2763282731377a11cee94fb744bb1e30ca71a05))
- Implement diametrization models (kanari - [2ac2fef](https://github.com/BlueBrain/NeuroTS/commit/2ac2feffa7503082d41d61b3604a1652d8295f74))
- Refactor section.py (Benoît Coste - [df98551](https://github.com/BlueBrain/NeuroTS/commit/df9855107d6d49a71c42f9e22d8e3753e184df35))
- Correct small issues. Include new algorithm to identify apical_point_distance (kanari - [d457864](https://github.com/BlueBrain/NeuroTS/commit/d4578646d5a77084024ba5c696590270344205de))
- Updated tox.ini (Arseny V. Povolotsky - [82b282b](https://github.com/BlueBrain/NeuroTS/commit/82b282b8221d18f34df8fcf7693d0f2f61fcf86d))
- Correct format (kanari - [93290b3](https://github.com/BlueBrain/NeuroTS/commit/93290b39544e91b6a57276e37ce2c094e5746a1a))
- Correct bugs in code and remove unused code (kanari - [e8769ab](https://github.com/BlueBrain/NeuroTS/commit/e8769abb979aabae32a7d80ffa4b9d22acb719af))
- Activate tox -e py27/35 (Benoît Coste - [d4713f9](https://github.com/BlueBrain/NeuroTS/commit/d4713f95a5f2339d285c2f2c0e04ff8b56f0679f))
- Fix TMD version and update README (Benoît Coste - [0266d21](https://github.com/BlueBrain/NeuroTS/commit/0266d2163b098550d0817692f04ee6115ffee594))
- Reduce exp overflow occurrence rate (Arseny V. Povolotsky - [a446abe](https://github.com/BlueBrain/NeuroTS/commit/a446abebe6037276cdfcd241d8bbdc6e9aba0c8f))
- Reduce exp overflow occurrence rate - 2 (Arseny V. Povolotsky - [aa32258](https://github.com/BlueBrain/NeuroTS/commit/aa322582fc0e360882998fa42ec2c241825815b1))
- Release tns==1.0.3 (Arseny V. Povolotsky - [816a49e](https://github.com/BlueBrain/NeuroTS/commit/816a49ee54b0464116e3afaa1ac782942626462f))
- Use dev version (Benoît Coste - [848d9fe](https://github.com/BlueBrain/NeuroTS/commit/848d9fe0da6e42b3d11b875774ee48365ca59d47))

## [1.0.2](https://github.com/BlueBrain/NeuroTS/compare/1.0.1..1.0.2)

> 12 December 2018

- Use Morphio 2.0 (Benoît Coste - [fc36ed5](https://github.com/BlueBrain/NeuroTS/commit/fc36ed5ee33657dbccfbd7d387bbd9fdc8c15390))
- Bump version (Benoît Coste - [09830f3](https://github.com/BlueBrain/NeuroTS/commit/09830f37aedac56e434133cee0b632f44a668c2a))

## 1.0.1

> 11 December 2018

- Migration of Topological Neuron Synthesis from bitbucket (Lida Kanari - [8ad9ec1](https://github.com/BlueBrain/NeuroTS/commit/8ad9ec1766e9c6541e52fe932c81ca3081a73cbc))
- Cleaning up directories and restructuring. The new code implements the basic growth algorithms: trunk, tmd, tmd_apical-mockup. To be extended to include more algorithms in future versions. (kanari - [8154929](https://github.com/BlueBrain/NeuroTS/commit/8154929de47beeb643ff1c2185ee5788bc08d905))
- Ongoing refactoring of internal algorithms. (Lida Kanari - [29e658b](https://github.com/BlueBrain/NeuroTS/commit/29e658b92aaa9c6b505f86ce93bf8edc7fb007fa))
- Adding MorphIO + neurites now grow in parallel (kanari - [134627a](https://github.com/BlueBrain/NeuroTS/commit/134627a69043eed7909c3beaaa3ac25801efb40b))
- Further cleaning up of code in lower level functionality (Lida Kanari - [09c8fa9](https://github.com/BlueBrain/NeuroTS/commit/09c8fa91590932797730f7f561d6cb50871f61d8))
- Cleaning up code: stage 1 (Lida Kanari - [a312ad0](https://github.com/BlueBrain/NeuroTS/commit/a312ad095f7a4d736ea6913ab98c15e7dbaaa550))
- Cleaning-up basic functionality. Add path distance and gradient based growth. (kanari - [0ace7a6](https://github.com/BlueBrain/NeuroTS/commit/0ace7a6b222307a62dcdaa55826083fc2285a918))
- Cleaning up basic growers (kanari - [8584048](https://github.com/BlueBrain/NeuroTS/commit/85840489d99ca6ead7cfcea67b7d4f53360597bf))
- Improve performances (Benoît Coste - [ce3d6e2](https://github.com/BlueBrain/NeuroTS/commit/ce3d6e293f82c155b7dac53a96021728e7476f2c))
- Corrections on angles (kanari - [11702e3](https://github.com/BlueBrain/NeuroTS/commit/11702e3c9bd1d79ec623e9c8f1530fea74f4c840))
- Data to be tested in future versions (Lida Kanari - [f95174e](https://github.com/BlueBrain/NeuroTS/commit/f95174ea76495190b5dd1119d7703a305bdda69a))
- Empty commit to test devpy packaging (Benoît Coste - [f95a1c0](https://github.com/BlueBrain/NeuroTS/commit/f95a1c000b420ffd73ab0e308185fa0453eeb36a))
- Cleanup code to make tox work (Benoît Coste - [baa0f7d](https://github.com/BlueBrain/NeuroTS/commit/baa0f7d3d5d9749fcf4eb6dfae7dacbf00dd1529))
- Fix bugs in code and clean up input parameters in growers (kanari - [1338af8](https://github.com/BlueBrain/NeuroTS/commit/1338af88e3fd532b04c9fd0f03d5a0f4bb0e11ea))
- Recover apical growth (kanari - [c9631dd](https://github.com/BlueBrain/NeuroTS/commit/c9631dd552f6543db6aea1413dd5039eabfc26fc))
- Add the ability to modify barcode according to external function, this is useful for growing cells inside an Atlas (kanari - [82f8e1e](https://github.com/BlueBrain/NeuroTS/commit/82f8e1e8c758ff0db16f847d666c42663e7b5928))
- Fix morphIO new API (Benoit Coste - [7a28905](https://github.com/BlueBrain/NeuroTS/commit/7a28905e18a69ad0156364802cbdd57150378ba4))
- Remove unnecessary naming of neuron (Lida Kanari - [52dc764](https://github.com/BlueBrain/NeuroTS/commit/52dc7647b088cd8a2ca3c0e81e8f4a6260ff28bd))
- Add valid bio example (Lida Kanari - [566a3e3](https://github.com/BlueBrain/NeuroTS/commit/566a3e3247ef448aabf271aec7a0d1ebc52d8959))
- Installation instructions (Lida Kanari - [18b8886](https://github.com/BlueBrain/NeuroTS/commit/18b88868155cd1f152e5a1e211678c4784e7da40))
- Minor corrections to pip install (Lida Kanari - [169d002](https://github.com/BlueBrain/NeuroTS/commit/169d002e04b61abcaef6405013f4c8730c72926b))
- Simplify install instructions (Benoit Coste - [ef6e659](https://github.com/BlueBrain/NeuroTS/commit/ef6e6595cccc72c5acda0abaec3023bde03b6f75))
- Update to tmd directory (Lida Kanari - [040ee8b](https://github.com/BlueBrain/NeuroTS/commit/040ee8b9d024b868f55c1f54b6018bc668278827))
- Add examples and test data (Lida Kanari - [4c13ca0](https://github.com/BlueBrain/NeuroTS/commit/4c13ca0ce70c99b3f4da890b82b9edf2910c7cf1))
- Update examples to consume test_data (Lida Kanari - [02c86d7](https://github.com/BlueBrain/NeuroTS/commit/02c86d779b4250f8a45d99f86a1699eb53d3c068))
- Fix small issue in section direction (kanari - [9c9c71d](https://github.com/BlueBrain/NeuroTS/commit/9c9c71d457b78c17607a888b47a724f7d4b0f7e4))
- Bump version number (Benoît Coste - [740e3e8](https://github.com/BlueBrain/NeuroTS/commit/740e3e8b46f4fdc046f7bc7ed3109049f6d089a2))
- Fix setup.py (Benoît Coste - [e3bf523](https://github.com/BlueBrain/NeuroTS/commit/e3bf523ff68ff274f7fc6e618afaee0c9957929c))
- Use correct version number (Benoît Coste - [3ba1d51](https://github.com/BlueBrain/NeuroTS/commit/3ba1d513e7cd5bec0c747c0f740084c25c545e58))
- Update setup.py and installation docs (Lida Kanari - [c4ee674](https://github.com/BlueBrain/NeuroTS/commit/c4ee6743a8d14e8bb261d766683bfbc017bf89cf))
- Commit to work on this (kanari - [9934a0a](https://github.com/BlueBrain/NeuroTS/commit/9934a0ab1c153bd0a13643d98ac5605631212641))
- Example for full synthesis of a cell (Lida Kanari - [f6a38d2](https://github.com/BlueBrain/NeuroTS/commit/f6a38d29e903909c73d78447848e422e6b1b3ee1))
- Update to tmd directory (Lida Kanari - [dd847e4](https://github.com/BlueBrain/NeuroTS/commit/dd847e4661d17f1556082f4ec44387d9519474ea))
- Fix small issue in section direction (kanari - [97d7c93](https://github.com/BlueBrain/NeuroTS/commit/97d7c939a0d84a39b3f4417b67d9ae1229c7c746))
- Bump version (Benoît Coste - [b4a9ecc](https://github.com/BlueBrain/NeuroTS/commit/b4a9ecc86e995f464c97a1e9f5ac0d95c482ed80))
- sorry (Eleftherios Zisis - [afe12d4](https://github.com/BlueBrain/NeuroTS/commit/afe12d45f254f157aac8d2fcc95133984d28a878))
- test_commit (Eleftherios Zisis - [1ee9251](https://github.com/BlueBrain/NeuroTS/commit/1ee92511851979b3b3ab6b5c5faad1b1c23fd748))
- Add some test files (Lida Kanari - [aaabb81](https://github.com/BlueBrain/NeuroTS/commit/aaabb8181e85fcddf7e5e4736599e4c2db73cc77))
- Initial empty repository (Julien Francioli - [e638bc7](https://github.com/BlueBrain/NeuroTS/commit/e638bc7684097ad9da70ed8960e4ecbeebfc5a9d))
