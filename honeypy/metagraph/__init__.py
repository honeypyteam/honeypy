"""Metagraph package: concrete node abstractions.

This package provides concrete, framework-level abstractions that build on the
meta layer. It exposes the primary node types used in the metagraph model:

- HoneyPoint
  Lightweight data/point wrapper (typically a single record/row).
- HoneyFile
  File-like node that yields HoneyPoint items; may represent virtual or
  physical files and supports custom loading/unloading.
- HoneyCollection
  Directory/collection node that groups HoneyFile instances and provides
  collection-level loading and metadata.

These classes are small ABCs intended to be subclassed by project-specific
implementations (fixtures, test helpers, or real backends). They rely on the
core lifecycle/metadata contract defined in the meta package.
"""

from .honey_collection import HoneyCollection
from .honey_file import HoneyFile
from .honey_point import HoneyPoint
from .meta.honey_node import HoneyNode

__all__ = ["HoneyPoint", "HoneyFile", "HoneyCollection", "HoneyNode"]

__author__ = "Lawrence Borst"
__email__ = "laurens.s.borst@gmail.com"
