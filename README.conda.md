About pyeantic
==============

Home: https://github.com/flatsurf/pyeantic

Package license: LGPL3

Feedstock license: BSD 3-Clause

Summary: Python Wrapper for E-ANTIC



Current build status
====================


<table>
    
  <tr>
    <td>Azure</td>
    <td>
      <details>
        <summary>
          <a href="https://dev.azure.com/flatsurf/conda/_build/latest?definitionId=&branchName=master">
            <img src="https://dev.azure.com/flatsurf/conda/_apis/build/status/pyeantic-feedstock?branchName=master">
          </a>
        </summary>
        <table>
          <thead><tr><th>Variant</th><th>Status</th></tr></thead>
          <tbody><tr>
              <td>linux</td>
              <td>
                <a href="https://dev.azure.com/flatsurf/conda/_build/latest?definitionId=&branchName=master">
                  <img src="https://dev.azure.com/flatsurf/conda/_apis/build/status/pyeantic-feedstock?branchName=master&jobName=linux&configuration=linux_" alt="variant">
                </a>
              </td>
            </tr>
          </tbody>
        </table>
      </details>
    </td>
  </tr>
  <tr>
    <td>OSX</td>
    <td>
      <img src="https://img.shields.io/badge/OSX-disabled-lightgrey.svg" alt="OSX disabled">
    </td>
  </tr>
  <tr>
    <td>Windows</td>
    <td>
      <img src="https://img.shields.io/badge/Windows-disabled-lightgrey.svg" alt="Windows disabled">
    </td>
  </tr>
![ppc64le disabled](https://img.shields.io/badge/ppc64le-disabled-lightgrey.svg)
</table>

Current release info
====================

| Name | Downloads | Version | Platforms |
| --- | --- | --- | --- |
| [![Conda Recipe](https://img.shields.io/badge/recipe-pyeantic-green.svg)](https://anaconda.org/flatsurf/pyeantic) | [![Conda Downloads](https://img.shields.io/conda/dn/flatsurf/pyeantic.svg)](https://anaconda.org/flatsurf/pyeantic) | [![Conda Version](https://img.shields.io/conda/vn/flatsurf/pyeantic.svg)](https://anaconda.org/flatsurf/pyeantic) | [![Conda Platforms](https://img.shields.io/conda/pn/flatsurf/pyeantic.svg)](https://anaconda.org/flatsurf/pyeantic) |

Installing pyeantic
===================

Installing `pyeantic` from the `flatsurf` channel can be achieved by adding `flatsurf` to your channels with:

```
conda config --add channels flatsurf
```

Once the `flatsurf` channel has been enabled, `pyeantic` can be installed with:

```
conda install pyeantic
```

It is possible to list all of the versions of `pyeantic` available on your platform with:

```
conda search pyeantic --channel flatsurf
```




Updating pyeantic-feedstock
===========================

If you would like to improve the pyeantic recipe or build a new
package version, please fork this repository and submit a PR. Upon submission,
your changes will be run on the appropriate platforms to give the reviewer an
opportunity to confirm that the changes result in a successful build. Once
merged, the recipe will be re-built and uploaded automatically to the
`flatsurf` channel, whereupon the built conda packages will be available for
everybody to install and use from the `flatsurf` channel.
Note that all branches in the conda-forge/pyeantic-feedstock are
immediately built and any created packages are uploaded, so PRs should be based
on branches in forks and branches in the main repository should only be used to
build distinct package versions.

In order to produce a uniquely identifiable distribution:
 * If the version of a package **is not** being increased, please add or increase
   the [``build/number``](https://conda.io/docs/user-guide/tasks/build-packages/define-metadata.html#build-number-and-string).
 * If the version of a package **is** being increased, please remember to return
   the [``build/number``](https://conda.io/docs/user-guide/tasks/build-packages/define-metadata.html#build-number-and-string)
   back to 0.

Feedstock Maintainers
=====================

* [@saraedum](https://github.com/saraedum/)
* [@videlec](https://github.com/videlec/)

