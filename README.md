[![Build Status](https://dev.azure.com/flatsurf/conda/_apis/build/status/flatsurf.pyeantic?branchName=master)](https://dev.azure.com/flatsurf/conda/_build/latest?definitionId=5&branchName=master)

## Python Wrapper for E-ANTIC

This repository implements a Python wrapper for
[E-ANTIC](https://github.com/videlec/e-antic) powered by
[cppyy](https://github.com/videlec/e-antic).

## Current Release Info

We build and release this package with every push to the master branch.

| Name | Downloads | Version | Platforms |
| --- | --- | --- | --- |
| [![Build](https://img.shields.io/badge/recipe-pyeantic-green.svg)](https://anaconda.org/flatsurf/pyeantic) | [![Conda Downloads](https://img.shields.io/conda/dn/flatsurf/pyeantic.svg)](https://anaconda.org/flatsurf/pyeantic) | [![Conda Version](https://img.shields.io/conda/vn/flatsurf/pyeantic.svg)](https://anaconda.org/flatsurf/pyeantic) | [![Conda Platforms](https://img.shields.io/conda/pn/flatsurf/pyeantic.svg)](https://anaconda.org/flatsurf/pyeantic) |

## Install with Conda

You can install this package with conda. Download and install [Miniconda](https://conda.io/miniconda.html), then run

```
conda config --add channels conda-forge
conda create -n pyeantic -c flatsurf pyeantic
conda activate pyeantic
```

## Run with binder in the Cloud

You can try out the projects in this repository in a very limited environment online by clicking the following links:

* **pyeantic** [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/flatsurf/pyeantic/master?filepath=binder%2FSample.pyeantic.ipynb)

## Build from the Source Code Repository

We are following a standard autoconf setup, i.e., you can create the wrapper
`src/pyeantic` with the following:

```
git clone --recurse-submodules https://github.com/flatsurf/pyeantic.git
cd pyeantic
./bootstrap
./configure
make
make check # to run our test suite
make install # to install into /usr/local
```

## Build from the Source Code Repository with Conda Dependencies

If you don't want to use your distribution's packages, you can provide the
dependencies with conda. Download and install
[Miniconda](https://conda.io/miniconda.html), then run

```
conda config --add channels conda-forge
conda config --add channels flatsurf # if you want to pull in the latest version of dependencies
conda create -n pyeantic-build cxx-compiler libtool automake e-antic
conda activate pyeantic-build
export CPPFLAGS="-isystem $CONDA_PREFIX/include"
export CFLAGS="$CPPFLAGS"
export LDFLAGS="-L$CONDA_PREFIX/lib -Wl,-rpath-link=$CONDA_PREFIX/lib"
export CC="ccache cc"
export CXX="ccache c++"
git clone --recurse-submodules https://github.com/flatsurf/pyeantic.git
cd pyeantic
./bootstrap
./configure --prefix="$CONDA_PREFIX"
make
```

## Build from the Source Code Repository with Conda

The conda recipe in `recipe/` is built automatically as part of our Continuous
Integration. If you want to build the recipe manually, something like the
following should work:

```
git clone --recurse-submodules https://github.com/flatsurf/pyeantic.git
cd pyeantic
conda activate root
conda config --add channels conda-forge
conda config --add channels flatsurf # if you want to pull in the latest version of dependencies
conda install conda-build conda-forge-ci-setup=2
export FEEDSTOCK_ROOT=`pwd`
export RECIPE_ROOT=${FEEDSTOCK_ROOT}/recipe
export CI_SUPPORT=${FEEDSTOCK_ROOT}/.ci_support
export CONFIG=linux_
make_build_number "${FEEDSTOCK_ROOT}" "${RECIPE_ROOT}" "${CI_SUPPORT}/${CONFIG}.yaml"
conda build "${RECIPE_ROOT}" -m "${CI_SUPPORT}/${CONFIG}.yaml" --clobber-file "${CI_SUPPORT}/clobber_${CONFIG}.yaml"
```

You can then try out the package that you just built with:
```
conda create -n pyeantic-test --use-local pyeantic
conda activate pyeantic-test
```

## Run Tests and Benchmark

`make check` runs all tests through the pytest interface.

## Maintainers

* [@saraedum](https://github.com/saraedum)
* [@videlec](https://github.com/videlec)
