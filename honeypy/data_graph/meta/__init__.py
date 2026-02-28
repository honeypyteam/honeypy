"""Meta package for the data graph core.

This package exposes the minimal, framework-level abstractions used by the
data graph model (the "meta" layer). It intentionally keeps a very small public
surface: the lightweight lifecycle/metadata contract used by concrete node
types such as files, collections and projects.

Exports
-------
HoneyNode
    Abstract base class providing load/unload/metadata and child management.
"""

from .honey_node import HoneyNode

__all__ = ["HoneyNode"]

__author__ = "Lawrence Borst"
__email__ = "laurens.s.borst@gmail.com"
