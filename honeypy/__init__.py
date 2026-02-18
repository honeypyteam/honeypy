"""HoneyPy — lightweight, extensible tooling for research data management.

Provides core metagraph types, plugin discovery and small transforms used to
compose research data pipelines.
"""

from .honeypy import HoneyPy
from .metagraph import (
    honey_collection,
    honey_file,
    honey_project,
    nd_collection,
    nd_file,
    nd_project,
)

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
