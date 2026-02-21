"""Project node types for the metagraph.

This module defines HoneyProject, a thin node wrapper representing a complete research
project, for instance encompassing the folders, files and associated transformations
for a single research paper.
"""

from typing import (
    Any,
    Generic,
    LiteralString,
    Mapping,
    TypeVar,
)

from honeypy.metagraph.honey_collection import HoneyCollection
from honeypy.metagraph.meta.honey_node import HoneyNode

C = TypeVar("C", bound=HoneyCollection, covariant=True)
M = TypeVar("M", bound=Mapping[str, Any])
L = TypeVar("L", bound=LiteralString)


class HoneyProject(Generic[L, M, C], HoneyNode[L, M, C]):
    """Represents a single project node containing HoneyCollection items."""
