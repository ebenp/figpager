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
    version="0.25",
    author="Eben Pendleton",
    author_email="4080051+ebenp@users.noreply.github.com",
    url="https://github.com/ebenp/figpager",
    project_urls={
        "Code": "https://github.com/ebenp/figpager",
        "Issue tracker": "https://github.com/ebenp/figpager/issues",
    },
    description=("A figure page creator class"),
    license="MIT",
    keywords="figure page matplotlib",
    packages=["figpager"],
    include_package_data=True,
    package_data={"figpager": ["page_layout/*.ini"],},
    install_requires=["matplotlib",],
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Framework :: Matplotlib",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
