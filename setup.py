#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os

from setuptools import find_packages, setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="figpager",
    version="0.1",
    author="Eben Pendleton",
    author_email="4080051+ebenp@users.noreply.github.com",
    description=("A figure pager class"),
    license="MIT",
    keywords="figure page matplotlib",
    url="",
    packages=["figpager"],
    include_package_data=True,
    package_data={"figpager": ["page_layout/*.ini"],},
    install_requires=["matplotlib",],
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
)
