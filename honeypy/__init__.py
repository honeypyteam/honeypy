"""HoneyPy — lightweight, extensible tooling for research data management.

Provides core data graph types, plugin discovery and small transforms used to
compose research data pipelines.
"""

from .data_graph import (
    honey_collection,
    honey_file,
    honey_project,
    nd_collection,
    nd_file,
    nd_project,
)
from .honeypy import HoneyPy

__all__ = [
    "HoneyPy",
    "honey_file",
    "honey_collection",
    "honey_project",
    "nd_file",
    "nd_collection",
    "nd_project",
]

__author__ = "Lawrence Borst"
__email__ = "laurens.s.borst@gmail.com"
