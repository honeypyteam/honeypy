"""Metagraph package: concrete node abstractions.

This package provides concrete, framework-level abstractions that build on the
meta layer. It exposes the primary node types used in the metagraph model:

- HoneyFile
  File-like node that yields objects; may represent virtual or
  physical files and supports custom loading/unloading.
- HoneyCollection
  Directory/collection node that groups HoneyFile instances and provides
  collection-level loading and metadata.
- HoneyProject
  Collection of collections, representing a single research project, such as
  a research paper.

These classes are small ABCs intended to be subclassed by project-specific
implementations (fixtures, test helpers, or real backends). They rely on the
core lifecycle/metadata contract defined in the meta package.
"""

from .honey_collection import HoneyCollection
from .honey_file import HoneyFile
from .honey_project import HoneyProject
from .meta.honey_node import HoneyNode
from .nd_collection import NDHoneyCollection
from .nd_file import NDHoneyFile
from .nd_project import NDHoneyProject

__all__ = [
    "HoneyNode",
    "HoneyFile",
    "HoneyCollection",
    "HoneyProject",
    "NDHoneyFile",
    "NDHoneyCollection",
    "NDHoneyProject",
]

__author__ = "Lawrence Borst"
__email__ = "laurens.s.borst@gmail.com"
