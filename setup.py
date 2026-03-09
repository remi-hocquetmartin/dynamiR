#!/usr/bin/env python3
"""
Setup configuration for DynamiR package installation.

This file allows installation via:
    pip install -e .
    python setup.py install
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dynamiR",
    version="1.0.0",
    author="Rémi Hocquet Martin",
    author_email="remi.hocquetmartin@icloud.com",
    description="microRNA Binding Site Analysis Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dynamiR",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.7",
    install_requires=[
        "biopython>=1.75",
    ],
    entry_points={
        "console_scripts": [
            "dynamiR=projet:main",
        ],
    },
    include_package_data=True,
    keywords="bioinformatics microRNA mRNA binding sites",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/dynamiR/issues",
        "Source": "https://github.com/yourusername/dynamiR",
        "Documentation": "https://github.com/yourusername/dynamiR/wiki",
    },
)
