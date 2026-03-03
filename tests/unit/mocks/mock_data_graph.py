from pathlib import Path
from typing import Dict
from uuid import UUID

from honeypy.data_graph.meta.constants import ROOT_UUID
from honeypy.services.datagraph.data_graph import DataGraph, DataGraphNode


class MockDataGraph(DataGraph):
    def __init__(self, nodes: Dict[UUID, DataGraphNode]):
        self.nodes = {}
        self._set_root()
        self.nodes[self._root].children = set(
            key for key, val in nodes.items() if val.principal_parent == ROOT_UUID
        )
        self.nodes = nodes
        self._root_meta_folder = Path(".")
