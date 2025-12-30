#!/usr/bin/env python
import re
from pathlib import Path

from setuptools import find_namespace_packages
from setuptools import setup


def read(*names, **kwargs):
    with Path(__file__).parent.joinpath(*names).open(encoding=kwargs.get("encoding", "utf8")) as fh:
        return fh.read()


setup(
    name="quads-lib",
    version="0.1.9",
    license="LGPL-3.0-only",
    description="Python client library for interacting with the QUADS API",
    long_description="{}\n{}".format(
        re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub("", read("README.rst")),
        re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst")),
    ),
    author="Gonzalo Rafuls",
    author_email="gonza@redhat.com",
    url="https://github.com/quadsproject/python-quads-lib",
    packages=find_namespace_packages("src"),
    package_dir={"": "src"},
    py_modules=[path.stem for path in Path("src").glob("*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": "https://python-quads-lib.readthedocs.io/",
        "Changelog": "https://python-quads-lib.readthedocs.io/en/latest/changelog.html",
        "Issue Tracker": "https://github.com/quadsproject/python-quads-lib/issues",
    },
    keywords=[
        # eg: "keyword1", "keyword2", "keyword3",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
    ],
    extras_require={
        # eg:
        #   "rst": ["docutils>=0.11"],
        #   ":python_version=='3.8'": ["backports.zoneinfo"],
    },
)
