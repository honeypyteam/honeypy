"""
Application bootstrap utilities.

This module provides a single entry point which wires together the core honeypy
services for a given project.
"""

from pathlib import Path
from typing import List

from honeypy.data_graph.meta.class_registry import register_node_class
from honeypy.data_graph.meta.honey_node import HoneyNode
from honeypy.services.context import HoneyContext
from honeypy.services.datagraph.data_graph import DataGraph


def bootstrap(
    node_classes: List[type["HoneyNode"]],
    root_location: Path,
) -> HoneyContext:
    """
    Bootstrap the application.

    This function builds the service objects, and scans the state of the project
    from the metadata.
    """
    _register_node_classes(node_classes)

    return _get_context(root_location)


def _get_context(root_meta_folder: Path) -> HoneyContext:
    data_graph = DataGraph(root_meta_folder)
    context = HoneyContext(data_graph)

    return context


def _register_node_classes(node_classes: List[type["HoneyNode"]]) -> None:
    for n_cls in node_classes:
        register_node_class(n_cls)
