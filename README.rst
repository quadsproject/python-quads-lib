========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - |github-actions| |codecov|
    * - package
      - |version| |wheel| |supported-versions| |supported-implementations|
.. |docs| image:: https://readthedocs.org/projects/python-quads-lib/badge/?style=flat
    :target: https://readthedocs.org/projects/python-quads-lib/
    :alt: Documentation Status

.. |github-actions| image:: https://github.com/quadsproject/python-quads-lib/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/quadsproject/python-quads-lib/actions

.. |codecov| image:: https://codecov.io/github/quadsproject/python-quads-lib/graph/badge.svg?token=E8NVWU7P67
    :alt: Coverage Status
    :target: https://codecov.io/github/quadsproject/python-quads-lib

.. |version| image:: https://img.shields.io/pypi/v/quads-lib.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/quads-lib

.. |wheel| image:: https://img.shields.io/pypi/wheel/quads-lib.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/quads-lib

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/quads-lib.svg
    :alt: Supported versions
    :target: https://pypi.org/project/quads-lib

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/quads-lib.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/quads-lib

.. end-badges

Python client library for interacting with the QUADS API

* Free software: GNU Lesser General Public License v3 (LGPLv3)

Installation
============

::

    pip install quads-lib

You can also install the in-development version with::

    pip install https://github.com/quadsproject/python-quads-lib/archive/development.zip


Documentation
=============


https://python-quads-lib.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    * - Command
      - ``PYTEST_ADDOPTS=--cov-append tox``
