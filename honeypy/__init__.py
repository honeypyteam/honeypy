"""HoneyPy: A lightweight, extensible framework for research data management.

This package provides a plugin architecture for managing research data, analyses,
and provenance. It serves as a core library that research teams can extend with
domain-specific functionality through plugins that inherit from the HoneyPy ABC.

The framework handles common research needs including data storage, anonymization,
transformation, analysis, and summarization across multiple datasets and projects.
"""

from .honeypy import HoneyPy
from .metagraph import (
    honey_collection,
    honey_file,
    honey_point,
    honey_project,
    nd_collection,
    nd_file,
    nd_project,
)

__all__ = [
    "HoneyPy",
    "honey_point",
    "honey_file",
    "honey_collection",
    "honey_project",
    "nd_file",
    "nd_collection",
    "nd_project",
]

__author__ = "Lawrence Borst"
__email__ = "laurens.s.borst@gmail.com"
