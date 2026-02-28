"""Enumeration of the different types of nodes."""

from enum import StrEnum


class NodeType(StrEnum):
    """
    Node types.

    Notes
    -----
    Here root nodes represent virtual nodes, a way to signify the "top" node of a
    project.

    Project nodes are, roughly speaking, one entire plugin. But a project can be a
    collection of projects if its corresponding plugin is composed of many plugins.

    Collections are collections of files, or collections of collections. They are
    roughly the same as folders in a filesystem.

    Files are roughly like files in a filesystem, but can also include several files.
    They encode the abstraction of a collection of rows following a given schema.

    Each of these node types can also be a product of said type.
    """

    ROOT = "root"
    PROJECT = "project"
    COLLECTION = "collection"
    FILE = "file"
